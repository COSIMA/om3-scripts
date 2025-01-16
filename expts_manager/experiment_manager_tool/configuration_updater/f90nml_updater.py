import os
import numpy as np
import f90nml
from experiment_manager_tool.utils.util_functions import get_namelist_group

class f90nmlUpdater:

    def update_nml_params(self, expt_path, param_dict, parameter_block, append_group_list: list =None, indx=None) -> None:
        """
        Updates namelist parameters and overwrites namelist file.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
            parameter_block (str): The name of the namelist file.
        """
        nml_path = os.path.join(expt_path, parameter_block)
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

        f90nmlUpdater._format_nml_params(nml_path, param_dict)

    @staticmethod
    def _format_nml_params(nml_path, param_dict):
        """
        Handles pre-formatted strings or values.

        Args:
            nml_path (str): The path to specific f90 namelist file.
            param_dict (dict): The dictionary of parameters to update.
            e.g., in yaml input file,
                ocean/input.nml:
                    mom_oasis3_interface_nml:
                        fields_in: "'u_flux', 'v_flux', 'lprec'"
                        fields_out: "'t_surf', 's_surf', 'u_surf'"
            results in,
                &mom_oasis3_interface_nml
                    fields_in = 'u_flux', 'v_flux', 'lprec'
                    fields_out = 't_surf', 's_surf', 'u_surf'
        """
        with open(nml_path, "r") as f:
            fileread = f.readlines()
        for tmp_group, tmp_subgroups in param_dict.items():
            for tmp_param, tmp_values in tmp_subgroups.items():
                # convert Python bool to Fortran logical
                if isinstance(tmp_values, bool):
                    tmp_values = ".true." if tmp_values else ".false."
                for i in range(len(fileread)):
                    if tmp_param in fileread[i]:
                        fileread[i] = f"    {tmp_param} = {tmp_values}\n"
                        break
        with open(nml_path, "w") as f:
            f.writelines(fileread)