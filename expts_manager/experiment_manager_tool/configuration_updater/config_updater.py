import os
import warnings
from utils.ryaml_handler import read_yaml, write_yaml
from configuration_updater.common import update_config_entries

class ConfigUpdater:
    @staticmethod
    def update_config_params(expt_path: str, param_dict: dict, filename):
        """
        Updates namelist parameters and overwrites namelist file.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
            filename (str): The name of the namelist file.
        """
        nml_path = os.path.join(expt_path, filename)
        expt_name = os.path.basename(expt_path)

        file_read = read_yaml(nml_path)
        if "jobname" in param_dict:
            if param_dict["jobname"] != expt_name:
                warnings.warn(
                    f"\n"
                    f"-- jobname must be the same as {expt_name}, "
                    f"hence jobname is forced to be {expt_name}!",
                    UserWarning,
                )
        param_dict["jobname"] = expt_name
        update_config_entries(file_read, param_dict)
        write_yaml(file_read, nml_path)
    
    @staticmethod
    def update_perturb_jobname(expt_path: str, expt_name: str) -> None:
        """
        Updates `jobname` only for now.
        Args:
            expt_path (str): The path to the perturbation experiment directory.
            expt_name (str): The name of the perturbation experiment.
        """
        config_path = os.path.join(expt_path, "config.yaml")
        config_data = read_yaml(config_path)
        config_data["jobname"] = expt_name
        write_yaml(config_data, config_path)