import subprocess

def get_git_url(file):
    """
    If the provided file is in a git repo, return the url to its most recent commit remote.origin.
    """
    dirname = os.path.dirname(file)

    try:
        url = subprocess.check_output(
            ["git", "-C", dirname, "config", "--get", "remote.origin.url"]
        ).decode("ascii").strip()
        url = url.removesuffix('.git')
    except subprocess.CalledProcessError:
        return None

    if url.startswith("git@github.com:"):
        url = f"https://github.com/{url.removeprefix('git@github.com:')}"

    top_level_dir = subprocess.check_output(
        ["git", "-C", dirname, "rev-parse", "--show-toplevel"]
    ).decode("ascii").strip()
    rel_path = file.removeprefix(top_level_dir)

    hash = subprocess.check_output(
        ["git", "-C", dirname, "rev-parse", "HEAD"]
    ).decode("ascii").strip()

    return f"{url}/blob/{hash}{rel_path}"

def git_status(file):
    """
    Return the git status of the file. Returns:
    - "unstaged" if the file has unstaged changes
    - "uncommitted" if the file has uncommited changes,
    - "unpushed" if the repo has unpushed commits
    - None otherwise
    """
    dirname = os.path.dirname(file)
    status = subprocess.check_output(
        ["git", "-C", dirname, "status", file]
    ).decode("ascii").strip()

    if "Changes not staged for commit" in status:
        return "unstaged"
    elif "Changes to be committed" in status:
        return "uncommitted"
    elif "Your branch is ahead" in status:
        return "unpushed"
    else:
        return None