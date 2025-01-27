"""
nuopc.runconfig Updater for the experiment management.

This module provides utilities for updating `nuopc.runconfig` configuration files.
It supports:
- Updating namelist parameters dynamically.
- Applying perturbation experiments.
- Ensuring compatibility with `om3utils`.

"""

import os
from access_om_expts.mixins.mixins import FullPathMixin, OM3UtilsLoaderMixin
from access_om_expts.configuration_updater.common import update_config_entries
from access_om_expts.utils.base_manager import BaseManager
from access_om_expts.utils.util_functions import (
    get_namelist_group,
    create_nested_dict,
)


class NuopcRunConfigUpdater(BaseManager, FullPathMixin, OM3UtilsLoaderMixin):
    """
    A utility class for updating `nuopc.runconfig` configuration file.

    Methods:
        - `update_runconfig_params`: Updates `nuopc.runconfig` parameters.
        - `update_nuopc_config_perturb`: Applies perturbation experiment configurations.
    """

    def __init__(self, yamlfile: str) -> None:
        """
        Initialises the `nuopc.runconfig` Updater.

        Args:
            yamlfile (str): Path to the YAML file containing experiment configuration.
        """
        super().__init__(yamlfile)

        # Load om3utils if required based on the model, e.g., "access-om3" from YAML input.
        self.load_om3utils_if_required(self.model)

    def update_runconfig_params(
        self,
        expt_path: str,
        param_dict: dict,
        filename: str,
        append_group_list: list = None,
        indx: int = None,
    ) -> None:
        """
        Updates parameters and overwrites the `nuopc.runconfig` file.

        Args:
            expt_path (str): Path to the experiment directory.
            param_dict (dict): Dictionary of parameters to update.
            filename (str): Name of the `nuopc.runconfig` file.
            append_group_list (list, optional): List of groups to append.
            indx (int, optional): Index to append to the group name if required.
        """
        nml_path = os.path.join(expt_path, filename)

        if indx is not None:
            nml_group = get_namelist_group(append_group_list, indx)
            param_dict = create_nested_dict(nml_group, param_dict)

        file_read = self.read_nuopc_config(nml_path)
        update_config_entries(file_read, param_dict)
        self.write_nuopc_config(file_read, nml_path)

    def update_nuopc_config_perturb(self, path):
        """
        Updates nuopc.runconfig for perturbation experiment runs.

        Args:
            path (str): Path to the experiment directory.
        """
        nuopc_input = self.indata.get("perturb_run_config")
        if nuopc_input is not None:
            nuopc_file_path = os.path.join(path, "nuopc.runconfig")
            nuopc_runconfig = self.read_nuopc_config(nuopc_file_path)
            update_config_entries(nuopc_runconfig, nuopc_input)
            self.write_nuopc_config(nuopc_runconfig, nuopc_file_path)
