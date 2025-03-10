"""
Utility Functions for the experiment management.

This module provides various helper functions used in experiment management.
It includes:
- Copying diagnostic tables to experiment directories.
- Handling namelist groups.
- Creating nested dictionaries.
"""

import subprocess
import os


def update_diag_table(path: str, diag_path: str, diag_flag: bool, model: str) -> None:
    """
    Updates the `diag_table` for the given experiment.

    Args:
        path (str): The experiment directory path.
        diag_path (str): The source directory containing `diag_table`.
        diag_flag (bool): If True, the diagnostic table will be copied.
        model (str): The model type (`access-om2` or `access-om3`).
    """
    if diag_flag and diag_path:
        if model == "access-om3":
            copy_diag_table(diag_path, path)
        elif model == "access-om2":
            # ocn_path: access-om2 specific path
            ocn_path = os.path.join(path, "ocean")
            copy_diag_table(diag_path, ocn_path)


def copy_diag_table(diag_path: str, path: str) -> None:
    """
    Copies the `diag_table` to the specified path.

    Args:
        diag_path (str): The source directory containing `diag_table`.
        path (str): The destination experiment directory.
    """
    if diag_path:
        command = f"scp {os.path.join(diag_path,'diag_table')} {path}"
        subprocess.run(command, shell=True, check=True)
        print(f"-- Copies diag_table to {path}")
    else:
        print(
            f"-- {diag_path} is not defined, hence skip copy `diag_table` to the experiment."
        )


def get_namelist_group(list_of_groupname: list[str], indx: int) -> str:
    """
    Retrieves the namelist group corresponding to the given index.

    Args:
        list_of_groupname (list[str]): List of namelist group names.
        indx (int): Index to retrieve from the list.

    Returns:
        str: The corresponding namelist group name.
    """
    nml_group = list_of_groupname[indx]
    return nml_group


def create_nested_dict(outer_key: str, inner_dict: dict[str, dict]) -> dict[str, dict]:
    """
    Creates a nested dictionary with the given outer key.

    Args:
        outer_key (str): The outer dictionary key.
        inner_dict (dict[str, dict]): The inner dictionary.

    Returns:
        dict[str, dict]: A nested dictionary structure.
    """
    return {outer_key: inner_dict}
