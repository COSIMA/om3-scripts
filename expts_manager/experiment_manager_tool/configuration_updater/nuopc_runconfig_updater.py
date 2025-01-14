import os
from mixins.mixins import FullPathMixin, OM3UtilsLoaderMixin
from configuration_updater.common import update_config_entries
from utils.base_manager import BaseManager
from utils.util_functions import get_namelist_group, create_nested_dict

class NuopcRunConfigUpdater(BaseManager, FullPathMixin, OM3UtilsLoaderMixin):
    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)

        # Load om3utils if required based on the model, e.g., "access-om3" from YAML input.
        self.load_om3utils_if_required(self.model)

    def update_runconfig_params(self, expt_path: str, param_dict: dict, parameter_block: str, append_group_list: list =None, indx: int =None) -> None:
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
            param_dict = create_nested_dict(nml_group, param_dict)

        file_read = self.read_nuopc_config(nml_path)
        update_config_entries(file_read, param_dict)
        self.write_nuopc_config(file_read, nml_path)

    @staticmethod
    def update_nuopc_config_perturb(self, path):
        """
        Updates nuopc.runconfig for perturbation experiment runs.
        """
        nuopc_input = self.indata.get("perturb_run_config")
        if nuopc_input is not None:
            nuopc_file_path = os.path.join(path, "nuopc.runconfig")
            nuopc_runconfig = self.read_nuopc_config(nuopc_file_path)
            self._update_config_entries(nuopc_runconfig, nuopc_input)
            self.write_nuopc_config(nuopc_runconfig, nuopc_file_path)