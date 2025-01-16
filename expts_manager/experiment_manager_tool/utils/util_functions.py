import subprocess
import os
from experiment_manager_tool.utils import constants

def update_diag_table(path: str, diag_path: str, diag_flag: bool, model: str) -> None:
    if diag_flag and diag_path:
        if model == "access-om3":
            copy_diag_table(diag_path, path)
        elif model == "access-om2":
            # ocn_path: access-om2 specific path
            ocn_path = os.path.join(path, "ocean")
            copy_diag_table(diag_path, ocn_path)

def copy_diag_table(diag_path: str, path: str) -> None:
    """
    Copies the diagnostic table (`diag_table`) to the specified path if a path is defined.
    """
    if diag_path:
        command = f"scp {os.path.join(diag_path,'diag_table')} {path}"
        subprocess.run(command, shell=True, check=True)
        print(f"-- Copies diag_table to {path}")
    else:
        print(f"-- {diag_path} is not defined, hence skip copy `diag_table` to the experiment.")
        
def get_namelist_group(list_of_groupname: list[str], indx: int) -> str:
    nml_group = list_of_groupname[indx]
    # rename the namlist by removing the suffix if the suffix with `_combo`
    if nml_group.endswith(constants.COMBO_SUFFIX):
        nml_group = nml_group[: -len(constants.COMBO_SUFFIX)]
    return nml_group

def create_nested_dict(outer_key: str, inner_dict: dict[str, dict]) -> dict[str, dict]:
    return {outer_key: inner_dict}