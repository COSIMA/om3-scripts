"""
Metadata Manager for the experiment management.

This module provides utilities for handling `metadata.yaml` updates.
It supports:
- Generating restart symlinks for perturbation experiments.
- Updating metadata descriptions and keywords.
- Ensuring consistency with control run metadata.
"""

import os
from access_om_expts.utils.ryaml_handler import (
    read_yaml,
    write_yaml,
    LiteralString,
)
from access_om_expts.manager import BASE_BRANCH_NAME


class MetaData:
    """
    A utility class for managing and updating metadata for perturbation experiments.

    This class provides methods for:
    - Generating restart symlinks.
    - Updating `metadata.yaml` with relevant keywords and descriptions.

    Methods:
        - `update_metadata`: Updates `metadata.yaml` with perturbation metadata.
        - `_generate_restart_symlink`: Creates a symlink to the restart directory.
        - `_update_metadata_yaml_perturb`: Updates metadata file with experiment details.
    """

    def __init__(
        self,
        startfrom_str: str,
        force_restart: bool,
        base_path: str,
        branch_perturb: str,
    ) -> None:
        """
        Initialises the metadata manager.

        Args:
            startfrom_str (str): Specifies the start condition (e.g., "rest").
            force_restart (bool): Whether to force recreation of the restart symlink.
            base_path (str): The base directory of the control experiment.
            branch_perturb (str): The branch name of the perturbation experiment.
        """
        self.startfrom_str = startfrom_str
        self.force_restart = force_restart
        self.base_path = base_path
        self.base_dir_name = os.path.dirname(self.base_path)
        self.branch_perturb = branch_perturb
        self.base_branch_name = BASE_BRANCH_NAME

    def update_medata(self, expt_path: str, param_dict: dict) -> None:
        """
        Updates metadata for a perturbation experiment.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): Dictionary containing parameter changes.
        """
        restartpath = self._generate_restart_symlink(expt_path)
        self._update_metadata_yaml_perturb(expt_path, param_dict, restartpath)

    def _generate_restart_symlink(self, expt_path: str) -> str:
        """
        Generates a symlink to the restart directory if needed.

        Args:
            expt_path (str): The path to the experiment directory.

        Returns:
            str: The restart path.
        """
        if self.startfrom_str != "rest":
            link_restart = os.path.join("archive", "restart" + self.startfrom_str)
            # restart dir from control experiment
            restartpath = os.path.realpath(os.path.join(self.base_path, link_restart))
            # restart dir symlink for each perturbation experiment
            dest = os.path.join(expt_path, link_restart)

            # only generate symlink if it doesnt exist or force_restart is enabled
            if (
                not os.path.islink(dest)
                or self.force_restart
                or (os.path.islink(dest) and not os.path.exists(os.readlink(dest)))
            ):
                if os.path.exists(dest) or os.path.islink(dest):
                    os.remove(dest)  # remove symlink
                    print(f"-- Remove restart symlink: {dest}")
                os.symlink(restartpath, dest)  # generate a new symlink
                if self.force_restart:
                    print(f"-- Restart symlink has been forced to be : {dest}")
                else:
                    print(f"-- Restart symlink: {dest}")
            # print restart symlink on the screen
            else:
                print(f"-- Restart symlink: {dest}")
        else:
            restartpath = "rest"
            print(f"-- Restart symlink: {restartpath}")

        return restartpath

    def _update_metadata_yaml_perturb(
        self, expt_path: str, param_dict: dict, restartpath: str
    ) -> None:
        """
        Updates the `metadata.yaml` file with relevant perturbation experiment.

        Args:
            expt_path (str): The path to the perturbation experiment directory.
            param_dict (dict): Dictionary of parameters to update.
            restartpath (str): The restart path.
        """
        metadata_path = os.path.join(expt_path, "metadata.yaml")
        metadata = read_yaml(metadata_path)
        self._update_metadata_description(metadata, restartpath)

        # remove None comments from `description`
        self._remove_metadata_comments("description", metadata)
        keywords = self._extract_metadata_keywords(param_dict)

        # extract parameters from the change list, and update `keywords`
        metadata["keywords"] = (
            f"{self.base_dir_name}, {self.branch_perturb}, {keywords}"
        )

        # remove None comments from `keywords`
        self._remove_metadata_comments("keywords", metadata)

        write_yaml(metadata, metadata_path)  # write to file

    def _remove_metadata_comments(self, key: str, metadata: dict) -> None:
        """
        Removes inline comments from metadata fields.

        Args:
            key (str): The key whose comments should be removed.
            metadata (dict): The metadata dictionary.
        """
        if key in metadata:
            metadata.ca.items[key] = [None, None, None, None]

    def _update_metadata_description(self, metadata: dict, restartpath: str) -> None:
        """
        Updates metadata description with control experiment details.

        Args:
            metadata (dict): The metadata dictionary.
            restartpath (str): The restart path.
        """
        tmp_string1 = (
            "\nNOTE: This is a perturbation experiment, "
            "but the description above is for the control run."
            f"\nThis perturbation experiment is based on the control run {self.base_path} "
            f"from {self.base_branch_name}"
        )
        tmp_string2 = f"\nbut with initial condition {restartpath}."

        desc = metadata.get("description", "")

        if desc is None:
            desc = ""
        if tmp_string1.strip() not in desc.strip():
            desc += tmp_string1
        if tmp_string2.strip() not in desc.strip():
            desc += tmp_string2

        metadata["description"] = LiteralString(desc)

    def _extract_metadata_keywords(self, param_change_dict):
        """
        Extracts keywords from parameter changes.

        Args:
            param_dict (dict): Dictionary of parameter changes.

        Returns:
            str: A comma-separated list of keywords.
        """
        return ", ".join(param_change_dict.keys())
