"""
MOM6 Parameter Updater for the experiment management.

This module provides utilities for updating MOM6 configuration files, including:
- Ensuring compatibility with `om3utils`.
- Modifying `MOM_input` parameters.
- Overriding parameters in `MOM_override`.
"""

import os
from typing import TYPE_CHECKING
from access_om_expts.utils.base_manager import BaseManager
from access_om_expts.mixins.mixins import FullPathMixin, OM3UtilsLoaderMixin

if TYPE_CHECKING:
    from om3utils import MOM6InputParser


class MOM6Updater(BaseManager, FullPathMixin, OM3UtilsLoaderMixin):
    """
    Handles updating MOM6 input and override parameter files.

    This class loads and modifies MOM6 configuration files for the experiment management.
    It dynamically loads `om3utils` if required, and provides methods to:
    - Update `MOM_input` parameters.
    - Override parameters in `MOM_override` with `#override` prefixes.
    """

    def __init__(self, yamlfile: str) -> None:
        """
        Initialises the MOM6Updater.

        Args:
            yamlfile (str): Path to the YAML file containing experiment configuration.
        """
        super().__init__(yamlfile)

        # Load om3utils if required based on the model, e.g., "access-om3" from YAML input.
        self.load_om3utils_if_required(self.model)

    def update_mom6_params(
        self, expt_path: str, param_dict_update: dict, filename: str
    ) -> None:
        """
        Updates MOM6 parameters in the `MOM_input` file.

        Args:
            expt_path (str): Path to the experiment directory.
            param_dict_update (dict): Dictionary of parameters to update.
            filename (str): filename, which is `MOM_input` for MOM6.
        """
        mom6_path = os.path.join(expt_path, filename)
        mom6_input_parser = self.parser_mom6_input(mom6_path)
        param_dict = mom6_input_parser.param_dict
        param_dict.update(param_dict_update)

        # overwrite to the same `MOM_input` file
        mom6_input_parser.writefile_MOM_input(mom6_path)

    def override_mom6_params(
        self, expt_path: str, param_dict: dict, commt_dict: dict
    ) -> None:
        """
        Updates MOM6 parameters in the `MOM_override` file.

        Args:
            expt_path (str): Path to the experiment directory.
            param_dict (dict): Dictionary of parameters to override.
            commt_dict (dict): Dictionary of comment changes for parameters.
        """
        mom6_override_parser = self.parser_mom6_input(
            os.path.join(expt_path, "MOM_override")
        )
        mom6_override_parser.param_dict, mom6_override_parser.commt_dict = (
            MOM6Updater.update_mom6_params_override(param_dict, commt_dict)
        )
        mom6_override_parser.writefile_MOM_input(
            os.path.join(expt_path, "MOM_override")
        )

    def parser_mom6_input(self, path: str) -> "MOM6InputParser":
        """
        Parses a MOM6 input file.

        Args:
            path (str): Path to the MOM_input file.

        Returns:
            MOM6InputParser: An instance of the MOM6 input parser.
        """
        mom6_parser = self.mom6_input_parser.MOM6InputParser()
        mom6_parser.read_input(path)
        mom6_parser.parse_lines()
        return mom6_parser

    @staticmethod
    def update_mom6_params_override(param_dict_change: dict, commt_dict: dict) -> tuple:
        """
        Prepends `#override` to parameters for MOM6.
        Args:
            param_dict_change (dict): dictionary of parameters to override
            commt_dict (dict): dictionary of comments for parameters
        Returns:
            tuple: Two dictionaries with `#override` prepended to each key.
        """
        override_param_dict_change = {
            f"#override {k}": v for k, v in param_dict_change.items()
        }
        override_commt_dict = {f"#override {k}": v for k, v in commt_dict.items()}
        return override_param_dict_change, override_commt_dict
