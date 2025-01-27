"""
PBS Job Management for the experiment management

This module provides utilities for managing PBS jobs, including:
- Checking for existing jobs.
- Handling duplicate submissions.
- Committing changes before execution.
- Starting new PBS runs.
"""

import os
import subprocess
import glob
from access_om_expts.git_manager.git_manager import check_and_commit_changes


class PBSJobManager:
    """
    Manages PBS jobs by checking for existing jobs, handling duplicates,
    committing changes to the repo, and starting new experiment runs.
    """

    def __init__(
        self, dir_manager: str, check_duplicate_jobs: bool, nruns: int
    ) -> None:
        """
        Initialises the PBSJobManager.

        Args:
            dir_manager (str): Directory manager for the experiments.
            check_duplicate_jobs (bool): Flag to enable or disable duplicate job detection.
            nruns (int): Number of runs for the experiment.
        """
        self.dir_manager = dir_manager
        self.nruns = nruns
        self.check_duplicate_jobs = check_duplicate_jobs

    def pbs_job_runs(self, path) -> None:
        """
        Manages PBS job runs by checking for existing jobs, handling duplicates,
        committing changes, and starting experiment runs if no duplication is detected.

        Args:
            path (str): Path to the experiment directory.
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
        TODO: When Setonix, Pawsey becomes available, explicitly include support by
        integrating `detect_hpc()` from the `__init__.py` module.

        Returns:
            dict: A dictionary containing PBS job information, where each key
                  is a job ID, and the value is a dictionary of job attributes.
        Raises:
            RuntimeError: If the PBS job status command fails.
        """
        current_job_status_path = os.path.join(".", "current_job_status")
        command = f"qstat -f > {current_job_status_path}"
        subprocess.run(command, shell=True, check=True)

        pbs_jobs = {}
        current_key = None
        current_value = ""
        job_id = None
        with open(current_job_status_path, "r", encoding="utf-8") as f:
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

        # Clean up the temporary file: `current_job_status`
        os.remove(current_job_status_path)

        return pbs_jobs

    def _check_duplicated_jobs(self, path: str, pbs_jobs: dict) -> bool:
        """
        Checks for duplicate running jobs in the same parent folder.

        Args:
            path (str): Path to the experiment directory.
            pbs_jobs (dict): Dictionary of current PBS jobs.

        Returns:
            bool: True if duplicate jobs are detected, otherwise False.
        """
        parent_paths = {}
        duplicated = False

        for _, job_info in pbs_jobs.items():
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
                    f"-- You have duplicated runs for '{os.path.basename(path)}'"
                    f"in the same folder '{parent_path}', "
                    "hence not submitting this job!\n"
                )
                duplicated = True

        return duplicated

    def _start_experiment_runs(self, path: str, duplicated: bool) -> None:
        """
        Starts the experiment runs if no duplicate jobs are detected.

        Args:
            path (str): Path to the experiment directory.
            duplicated (bool): Indicates whether duplicate jobs were found.
        """
        if duplicated:
            return

        # first clean `work` directory for failed jobs
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
                f"-- `{os.path.basename(path)}` already completed "
                f"{doneruns} runs, hence no new runs.\n"
            )

    def _clean_workspace(self, path: str) -> None:
        """
        Cleans `work` directory for failed jobs.

        Args:
            path (str): Path to the experiment directory.
        """
        work_dir = os.path.join(path, "work")
        # in case any failed job
        if os.path.islink(work_dir) and os.path.isdir(work_dir):
            # Payu sweep && setup to ensure the changes correctly && remove the `work` directory
            command = "payu sweep && payu setup"
            subprocess.run(command, shell=True, check=False)
            print(f"Clean up a failed job {work_dir} and prepare it for resubmission.")

    @staticmethod
    def _extract_current_and_parent_path(tmp_path: str) -> tuple:
        """
        Extracts the current (experiment) and parent (test) paths from a PBS job error path.

        Args:
            tmp_path (str): The error path from a PBS job.

        Returns:
            tuple: (experiment folder path, parent test folder path).
        """
        # extract current (base_name or expt_name) from pbs jobs
        folder_path = "/" + "/".join(tmp_path.split("/")[1:-1])

        # extract parent (test_path) from pbs jobs
        parent_path = "/" + "/".join(tmp_path.split("/")[1:-2])

        return folder_path, parent_path
