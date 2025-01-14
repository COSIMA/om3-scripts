import subprocess
import os
import git
from typing import Optional

def payu_clone_from_commit_hash(url: str, commit_hash: str, branch_name: str, path: str) -> None:
    """
    Clones a configuration using a specific commit hash and git url.
    
    Args:
        url (str): The url of the repo to clone.
        commit_hash (str): The commit hash to checkout.
        branch_name (str): The branch name to create.
        path (str): The local path where the repo should be cloned.

    Raises:
        RuntimeError: If the cloning process fails.
    """
    print(f"Cloning a configuration from {commit_hash} {url} to {path}")
    
    # https://github.com/payu-org/payu/pull/515
    command = f"payu clone -b {branch_name} -s {commit_hash} {url} {path}"
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"-- Successfully cloned {os.path.relpath(path)}")
    except RuntimeError as e:
        print(f"Error during cloning: {e}")
        raise

def check_and_commit_changes(path: str) -> None:
    """
    Checks the current state of the repo, stages relevant changes, and commits them.
    If no changes are detected, it provides a message indicating that no commit was made.
    """
    repo = git.Repo(path)
    current_branch = repo.active_branch.name
    print(f"-- Current branch for the control experiment is: {current_branch}")

    lock_file = os.path.join(repo.git_dir, 'index.lock')
    if os.path.exists(lock_file):
        os.remove(lock_file)

    # handle delete files
    if deleted_files := _get_deleted_files(repo):
        repo.index.remove(deleted_files, r=True)
        print(f"Removed deleted files: {deleted_files}")

    untracked_files = _get_untracked_files(repo)
    changed_files = _get_changed_files(repo)
    staged_files = set(untracked_files + changed_files)

    # restore *.swp files in case users open any files during an experiment is running.
    _restore_swp_files(repo, staged_files)

    commit_message = f"Control experiment setup: Configure `{current_branch}` branch,\ncommitted files/directories {staged_files}!"

    if staged_files:
        repo.index.add(staged_files)
        repo.index.commit(commit_message)
        print(f"Files/directories will be committed: {staged_files}.")
    else:
        print(f"-- Nothing changed, hence no further commits to {path}.")

def _get_deleted_files(repo: git.Repo) -> Optional[list[str]]:
    """
    Gets deleted git files.
    """
    return [file.a_path for file in repo.index.diff(None) if file.change_type == "D"]

def _get_changed_files(repo: git.Repo) -> Optional[list[str]]:
    """
    Gets changed git files.
    """
    return [file.a_path for file in repo.index.diff(None) if file.change_type != "D"]

def _get_untracked_files(repo: git.Repo) -> Optional[list[str]]:
    """
    Gets untracked git files.
    """
    return repo.untracked_files

def _restore_swp_files(repo: git.Repo, staged_files: list[str]) -> None:
    """
    Restores tmp git files.
    """
    swp_files = [file for file in staged_files if file.endswith(".swp")]
    for file in swp_files:
        repo.git.restore(file)