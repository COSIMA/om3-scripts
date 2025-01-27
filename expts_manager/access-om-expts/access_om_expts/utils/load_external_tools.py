"""
External Tools Manager for the experiment management.

This module provides utilities to manage external tools required for experiments,
including:
- Cloning `om3-utils` for the ACCESS-OM3 model.
- Cloning and updating diagnostic tables (`diag_table`).
- Handling forced overwrites of external repositories.
"""

import os
import warnings
import shutil
import subprocess
from access_om_expts.mixins.mixins import FullPathMixin
from access_om_expts.utils.base_manager import BaseManager


class ExternalTools(BaseManager, FullPathMixin):
    """
    A utility class for managing external tools required for experiments.

    This class handles:
    - Cloning `om3-utils` if required.
    - Cloning diagnostic tables.
    - Handling forced overwrites of external tools.

    Methods:
        - `clone_om3utils`: Clones `om3-utils` for the ACCESS-OM3 model.
        - `update_diag_table`: Clones or updates diagnostic tables.
    """

    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)
        self.utils_path = None
        self.diag_path = None
        self.force_overwrite_tools = self.indata.get("force_overwrite_tools")

    def clone_om3utils(self) -> None:
        """
        Clones `om3-utils` if required for the ACCESS-OM3 model.

        Raises:
            ValueError: If required parameters (`utils_url`,
                        `utils_dir_name`, `utils_branch_name`) are missing.
        """
        utils_url = self.indata.get("utils_url")
        utils_dir_name = self.indata.get("utils_dir_name")
        utils_branch_name = self.indata.get("utils_branch_name")

        if self.model == "access-om3":
            if not all([utils_url, utils_dir_name, utils_branch_name]):
                raise ValueError(
                    f"Missing required parameters for cloning {self.model}"
                )

            self.utils_path = self.full_path("utils_dir_name")
            ExternalTools._clone_repo(
                self.utils_path,
                utils_url,
                utils_branch_name,
                utils_dir_name,
                self.force_overwrite_tools,
            )

        elif self.model == "access-om2":
            warnings.warn(
                f"om3-utils tool is not required for {self.model}, "
                f"hence, skipping cloning!",
                UserWarning,
            )

    def update_diag_table(self) -> str | None:
        """
        Clones or updates the diagnostic table.

        Returns:
            str: Path to the diagnostic table directory.
        """

        diag_url = self.indata.get("diag_url")
        diag_branch_name = self.indata.get("diag_branch_name")
        diag_dir_name = self.indata.get("diag_dir_name")
        diag_path = self.full_path("diag_dir_name")

        if not any([diag_url, diag_dir_name, diag_branch_name]):
            print("Keep existing diag_table and hence skip cloning diag_table!")
            return self.diag_path

        ExternalTools._clone_repo(
            diag_path,
            diag_url,
            diag_branch_name,
            diag_dir_name,
            self.force_overwrite_tools,
        )
        return diag_path

    @staticmethod
    def _clone_repo(
        path: str,
        url: str,
        branch_name: str,
        tool_name: str,
        force_overwrite_tools: bool,
    ) -> None:
        """
        Clones a Git repository.

        Args:
            path (str): Local path where the repository should be cloned.
            url (str): Repository URL.
            branch_name (str): Branch to clone.
            tool_name (str): Name of the tool being cloned.
            force_overwrite_tools (bool): If True, forces overwrite of existing directory.

        Raises:
            RuntimeError: If cloning fails.
        """
        if os.path.exists(path) and os.path.isdir(path):
            if force_overwrite_tools:
                print(
                    f"-- Force_overwrite_tools, hence removing existing {tool_name}: {path}"
                )
                shutil.rmtree(path)
            else:
                print(
                    f"-- {tool_name} already exists at {path}, hence skipping cloning"
                )
                return
        print(f"Cloning {tool_name} from {url} (branch: {branch_name})...")

        try:
            command = [
                "git",
                "clone",
                "--branch",
                branch_name,
                url,
                path,
                "--single-branch",
            ]
            subprocess.run(command, check=True)
            print(f"-- Successfully cloned {tool_name} to {path}.")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr or e.stdout or "Unknown Git error"
            print(f"Failed to clone {tool_name}: {error_message.strip()}")
            raise RuntimeError(
                f"Cloning {tool_name} failed: {error_message.strip()}"
            ) from e
