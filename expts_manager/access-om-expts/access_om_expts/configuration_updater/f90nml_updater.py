"""
Fortran90 Namelist Updater for the experiment management.

This module provides utilities for updating F90 namelist (`.nml`, `_in`) files.
It supports:
- Patching parameter updates to existing namelist files.
- Formatting values correctly (including pre-formatted strings and logical booleans).
"""

import os
import numpy as np
import f90nml
from access_om_expts.utils.util_functions import get_namelist_group


class F90NMLUpdater:
    """
    A utility class for updating F90 namelist (`.nml`, '_in') configuration files.

    This class provides methods to patch parameter updates in namelist files while
    preserving formatting and ensuring correct Fortran syntax.

    Methods:
        - `update_nml_params`: Updates namelist parameters and patches the file.
        - `_format_nml_params`: Ensures proper formatting in the namelist file.
    """

    def update_nml_params(
        self,
        expt_path: str,
        param_dict: dict,
        filename: str,
        append_group_list: list = None,
        indx: int = None,
    ) -> None:
        """
        Updates namelist parameters and overwrites the namelist file.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
            filename (str): The name of the namelist file.
            append_group_list (list, optional): List of groups to append (if applicable).
            indx (int, optional): Index to append to the group name if required.
        """
        nml_path = os.path.join(expt_path, filename)
        if indx is not None:
            nml_group = get_namelist_group(append_group_list, indx)
            patch_dict = {nml_group: {}}
            for nml_name, nml_value in param_dict.items():
                if nml_name == "turning_angle":
                    cosw = np.cos(nml_value * np.pi / 180.0)
                    sinw = np.sin(nml_value * np.pi / 180.0)
                    patch_dict[nml_group]["cosw"] = cosw
                    patch_dict[nml_group]["sinw"] = sinw
                else:  # for generic parameters
                    patch_dict[nml_group][nml_name] = nml_value
            param_dict = patch_dict
            f90nml.patch(nml_path, param_dict, nml_path + "_tmp")
        else:
            f90nml.patch(nml_path, param_dict, nml_path + "_tmp")
        os.rename(nml_path + "_tmp", nml_path)

        F90NMLUpdater._format_nml_params(nml_path, param_dict)

    @staticmethod
    def _format_nml_params(nml_path: str, param_dict: dict) -> None:
        """
        Ensures proper formatting in the namelist file.

        This method correctly formats boolean values and ensures Fortran syntax
        is preserved when updating parameters.

        Args:
            nml_path (str): The path to specific f90 namelist file.
            param_dict (dict): The dictionary of parameters to update.
        Example:
            YAML input:
                ocean/input.nml:
                    mom_oasis3_interface_nml:
                        fields_in: "'u_flux', 'v_flux', 'lprec'"
                        fields_out: "'t_surf', 's_surf', 'u_surf'"

            Resulting `.nml` or `_in` file:
                &mom_oasis3_interface_nml
                    fields_in = 'u_flux', 'v_flux', 'lprec'
                    fields_out = 't_surf', 's_surf', 'u_surf'
        """
        with open(nml_path, "r", encoding="utf-8") as f:
            fileread = f.readlines()

        for _, tmp_subgroups in param_dict.items():
            for tmp_param, tmp_values in tmp_subgroups.items():
                # convert Python bool to Fortran logical
                if isinstance(tmp_values, bool):
                    tmp_values = ".true." if tmp_values else ".false."

                for idx, line in enumerate(fileread):
                    if tmp_param in line:
                        fileread[idx] = f"    {tmp_param} = {tmp_values}\n"
                        break

        with open(nml_path, "w", encoding="utf-8") as f:
            f.writelines(fileread)
