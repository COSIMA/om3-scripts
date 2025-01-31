"""
Base Manager for the experiment management.

This module provides a base class that initialises shared attributes and
loads variables from a YAML configuration file.
"""

import os
from access_om_expts.utils.ryaml_handler import read_yaml


class BaseManager:
    """
    A base class that initialises shared attributes and loads experiment configuration.

    This class provides common functionality for handling YAML-based configurations,
    ensuring consistency across different experiment managers.

    Attributes:
        yamlfile (str): Path to the YAML configuration file.
        dir_manager (str): The current working directory.
        test_path (str): Path for test experiments.
        model (str): The experiment model type.
        run_namelists (bool): Whether namelists are included in the experiment.

    Methods:
        - `_load_variables`: Loads configuration variables from the YAML file.
    """

    def __init__(self, yamlfile: str) -> None:
        """
        Initialises the BaseManager and loads experiment attributes.

        Args:
            yamlfile (str): Path to the YAML configuration file.
        """
        self.yamlfile = yamlfile
        self.dir_manager = os.getcwd()
        self._load_variables(self.yamlfile)

    def _load_variables(self, yamlfile: str) -> None:
        """
        Loads variables from the YAML configuration file.

        Args:
            yamlfile (str): Path to the YAML configuration file.
        """
        self.indata = read_yaml(yamlfile)
        self.dir_manager = os.getcwd()
        self.test_path = self.indata.get("test_path")
        self.model = self.indata.get("model")
        self.run_namelists = self.indata.get("run_namelists", False)
