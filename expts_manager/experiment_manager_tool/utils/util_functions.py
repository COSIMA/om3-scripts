import subprocess
import os


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
        print(
            f"-- {diag_path} is not defined, hence skip copy `diag_table` to the experiment."
        )


def get_namelist_group(list_of_groupname: list[str], indx: int) -> str:
    nml_group = list_of_groupname[indx]
    return nml_group


def create_nested_dict(outer_key: str, inner_dict: dict[str, dict]) -> dict[str, dict]:
    return {outer_key: inner_dict}
