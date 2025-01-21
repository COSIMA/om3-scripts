import os
import subprocess
import glob
from experiment_manager_tool.git_manager.git_manager import check_and_commit_changes


class PBSJobManager:
    """
    Manages PBS jobs by checking for existing jobs, handling duplicates,
    committing changes to the repo, and starting new experiment runs.
    """

    def __init__(
        self, dir_manager: str, check_duplicate_jobs: bool, nruns: int
    ) -> None:
        self.dir_manager = dir_manager
        self.nruns = nruns
        self.check_duplicate_jobs = check_duplicate_jobs

    def pbs_job_runs(self, path) -> None:
        """
        Main method to manage PBS job runs. It checks for existing jobs, handles duplicates,
        commits changes, and starts experiment runs if no duplication is detected.
        """
        # check existing pbs jobs
        pbs_jobs = PBSJobManager.output_existing_pbs_jobs()

        # check for duplicated running jobs
        if self.check_duplicate_jobs:
            duplicated_bool = self._check_duplicated_jobs(path, pbs_jobs)
        else:
            duplicated_bool = False

        if not duplicated_bool:
            # Checks the current state of the repo, commits relevant changes.
            check_and_commit_changes(path)

        # start control runs, count existing runs and do additional runs if needed
        self._start_experiment_runs(path, duplicated_bool)

    @staticmethod
    def output_existing_pbs_jobs() -> dict:
        """
        Retrieves and parses the current PBS job status using the `qstat -f` command.

        Returns:
            dict: A dictionary containing PBS job information, where each key
                  is a job ID, and the value is a dictionary of job attributes.
        """
        current_job_status_path = os.path.join(".", "current_job_status")
        command = f"qstat -f > {current_job_status_path}"
        subprocess.run(command, shell=True, check=True)

        pbs_jobs = {}
        current_key = None
        current_value = ""
        job_id = None
        with open(current_job_status_path, "r") as f:
            pbs_job_file = f.read()

        pbs_job_file = pbs_job_file.replace("\t", "        ")

        for line in pbs_job_file.splitlines():
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("Job Id:"):
                job_id = line.split(":", 1)[1].strip()
                pbs_jobs[job_id] = {}
                current_key = None
                current_value = ""
            elif line.startswith("        ") and current_key:  # 8 indents multi-line
                current_value += line.strip()
            elif line.startswith("    ") and " = " in line:  # 4 indents for new pair
                # Save the previous multi-line value
                if current_key:
                    pbs_jobs[job_id][current_key] = current_value.strip()
                key, value = line.split(" = ", 1)  # save key
                current_key = key.strip()
                current_value = value.strip()

        # Clean up the temporary `current_job_status`
        os.remove(current_job_status_path)

        return pbs_jobs

    def _check_duplicated_jobs(self, path: str, pbs_jobs: dict) -> bool:
        """
        Checks for duplicated running jobs in the same parent folder.

        Args:
            pbs_jobs (dict): Dictionary of current PBS jobs.

        Returns:
            bool: True if duplicate jobs are detected, otherwise False.
        """
        parent_paths = {}
        duplicated = False

        for job_id, job_info in pbs_jobs.items():
            folder_path, parent_path = PBSJobManager._extract_current_and_parent_path(
                job_info["Error_Path"]
            )
            job_state = job_info["job_state"]
            if job_state not in ("F", "S"):
                if parent_path not in parent_paths:
                    parent_paths[parent_path] = []
                parent_paths[parent_path].append(folder_path)

        for parent_path, folder_paths in parent_paths.items():
            if path in folder_paths:
                print(
                    f"-- You have duplicated runs for '{os.path.basename(path)}' in the same folder '{parent_path}', "
                    f"hence not submitting this job!\n"
                )
                duplicated = True

        return duplicated

    def _start_experiment_runs(self, path: str, duplicated: bool) -> None:
        """
        Starts the experiment runs if no duplicate jobs are detected.

        Args:
            duplicated (bool): Indicates whether duplicate jobs were found.
        """
        if duplicated:
            return

        # clean `work` directory for failed jobs
        self._clean_workspace(path)

        doneruns = len(
            glob.glob(os.path.join(path, "archive", "output[0-9][0-9][0-9]*"))
        )
        newruns = self.nruns - doneruns
        if newruns > 0:
            print(f"\nStarting {newruns} new experiment runs\n")
            command = f"cd {path} && payu run -n {newruns} -f"
            subprocess.run(command, shell=True, check=True)
            print("\n")
        else:
            print(
                f"-- `{os.path.basename(path)}` already completed {doneruns} runs, hence no new runs.\n"
            )

    def _clean_workspace(self, path):
        """
        Cleans `work` directory for failed jobs.
        """
        work_dir = os.path.join(path, "work")
        # in case any failed job
        if os.path.islink(work_dir) and os.path.isdir(work_dir):
            # Payu sweep && setup to ensure the changes correctly && remove the `work` directory
            command = f"payu sweep && payu setup"
            subprocess.run(command, shell=True, check=False)
            print(f"Clean up a failed job {work_dir} and prepare it for resubmission.")

    @staticmethod
    def _extract_current_and_parent_path(tmp_path):
        # extract current (base_name or expt_name) from pbs jobs
        folder_path = "/" + "/".join(tmp_path.split("/")[1:-1])

        # extract parent (test_path) from pbs jobs
        parent_path = "/" + "/".join(tmp_path.split("/")[1:-2])

        return folder_path, parent_path
