import os
import sys
import warnings
import shutil
import subprocess
from mixins.mixins import FullPathMixin
from utils.base_manager import BaseManager

class ExternalTools(BaseManager, FullPathMixin):
    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)
        self.utils_path = None
        self.diag_path = None
        self.force_overwrite_tools = self.indata.get("force_overwrite_tools")

    def clone_om3utils(self) -> None:
        """
        Clones external tools if necessary.

        Args:
            dir_manager (str)
        """
        utils_url = self.indata.get("utils_url")
        utils_dir_name = self.indata.get("utils_dir_name")
        utils_branch_name = self.indata.get("utils_branch_name")

        if self.model == "access-om3":
            if not all([utils_url, utils_dir_name, utils_branch_name]):
                raise ValueError(f"Missing required parameters for cloning {self.model}")

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

    def update_diag_table(self) -> str:
        """
        Clones external tools if necessary.
        
        Args:
            dir_manager (str)
        """

        diag_url = self.indata.get("diag_url")
        diag_branch_name = self.indata.get("diag_branch_name")
        diag_dir_name = self.indata.get("diag_dir_name")
        diag_path = self.full_path("diag_dir_name")

        if not any([diag_url, diag_dir_name, diag_branch_name]):
            print("Keep existing diag_table and hence skip cloning diag_table!")
            return

        ExternalTools._clone_repo(
            diag_path,
            diag_url,
            diag_branch_name,
            diag_dir_name,
            self.force_overwrite_tools,
        )
        return diag_path

    @staticmethod
    def _clone_repo(path: str, url: str, branch_name: str, tool_name: str, force_overwrite_tools: bool) -> None:
        if os.path.exists(path) and os.path.isdir(path):
            if force_overwrite_tools:
                print(f"-- Force_overwrite_tools, hence removing existing {tool_name}: {path}")
                shutil.rmtree(path)
            else:
                print(f"-- {tool_name} already exists at {path}, hence skipping cloning")
                return 
        print(f"Cloning {tool_name} from {url} (branch: {branch_name})...")

        try:
            command = (
                f"git clone --branch {branch_name} {url} {path} --single-branch"
            )
            subprocess.run(command, shell=True, check=True)
            print(f"-- Successfully cloned {tool_name} to {path}.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {tool_name}: {e.stderr.decode().strip()}")
            raise RuntimeError(f"Cloning {tool_name} failed") from e