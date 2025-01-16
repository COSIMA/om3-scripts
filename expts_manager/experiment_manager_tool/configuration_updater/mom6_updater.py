import os
from experiment_manager_tool.utils.base_manager import BaseManager
from experiment_manager_tool.mixins.mixins import FullPathMixin, OM3UtilsLoaderMixin

class MOM6Updater(BaseManager, FullPathMixin, OM3UtilsLoaderMixin):
    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)

        # Load om3utils if required based on the model, e.g., "access-om3" from YAML input.
        self.load_om3utils_if_required(self.model)
    
    def update_mom6_params(self, expt_path, param_dict_update, parameter_block):
        mom6_path = os.path.join(expt_path, parameter_block)
        MOM_inputParser = self._parser_mom6_input(mom6_path)
        param_dict = MOM_inputParser.param_dict
        param_dict.update(param_dict_update)
        # overwrite to the same `MOM_input` file
        MOM_inputParser.writefile_MOM_input(mom6_path)

    def override_mom6_params(self, expt_path, param_dict, commt_dict_change):
        #raise NotImplementedError("This method must be implemented")
        """
        Updates MOM6 parameters in the 'MOM_override' file. 'or': override

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
        """
        MOM6_or_parser = self._parser_mom6_input(
            os.path.join(expt_path, "MOM_override")
        )
        MOM6_or_parser.param_dict, MOM6_or_parser.commt_dict = (
            MOM6Updater.update_MOM6_params_override(param_dict, commt_dict_change)
        )
        MOM6_or_parser.writefile_MOM_input(os.path.join(expt_path, "MOM_override"))

    def _parser_mom6_input(self, path):
        """
        Parses MOM6 input file.
        """
        mom6parser = self.MOM6InputParser.MOM6InputParser()
        mom6parser.read_input(path)
        mom6parser.parse_lines()
        return mom6parser

    @staticmethod
    def update_MOM6_params_override(param_dict_change, commt_dict_change):
        """
        Prepends `#override` to parameters for MOM6.
        Args:
            param_dict_change (dict): dictionary of parameters to override
            commt_dict_change (dict): dictionary of comments for parameters
        Returns:
            tuple: Two dictionaries with `#override` prepended to each key.
        """
        override_param_dict_change = {
            f"#override {k}": v for k, v in param_dict_change.items()
        }
        override_commt_dict_change = {
            f"#override {k}": v for k, v in commt_dict_change.items()
        }
        return override_param_dict_change, override_commt_dict_change
