"""
Experiment Manager for the experiment management.

This module manages the execution of control and perturbation experiments.
It handles:
- Creating test directories.
- Ensuring model selection.
- Managing external tool dependencies.
- Running control and perturbation experiments.
"""

import os
from access_om_expts.utils.load_external_tools import ExternalTools
from access_om_expts.manager.control_experiment import ControlExperiment
from access_om_expts.manager.perturb_experiment import PerturbExperiment
from access_om_expts.utils.base_manager import BaseManager


class ExperimentManager(BaseManager):
    """
    Manages the execution of control and perturbation experiments.

    This class:
    - Ensures proper model selection.
    - Sets up external tools.
    - Runs control and perturbation experiments.

    Attributes:
        yamlfile (str): The path to the YAML configuration file.
        external_tools (ExternalTools): Manages external tool dependencies.
        control_experiment (ControlExperiment): Manages control experiments.
        perturb_experiment (PerturbExperiment): Manages perturbation experiments.

    Methods:
        - `create_test_path`: Creates the test directory for parameter testing.
        - `model_selection`: Ensures the model type is valid.
        - `run`: Executes the experiment workflow.
    """

    def __init__(self, yamlfile) -> None:
        """
        Initialises the ExperimentManager.

        Args:
            yamlfile (str): Path to the YAML configuration file.
        """
        super().__init__(yamlfile)
        self.yamlfile = yamlfile
        self.external_tools = None
        self.control_experiment = None
        self.perturb_experiment = None

    def create_test_path(self) -> None:
        """
        Creates the local test directory for parameter testing.
        """
        if os.path.exists(self.test_path):
            print(f"-- Test directory {self.test_path} already exists!")
        else:
            os.makedirs(self.test_path)
            print(f"-- Test directory {self.test_path} has been created!")

    def model_selection(self) -> None:
        """
        Ensures the selected model is either 'access-om2' or 'access-om3'.

        Raises:
            ValueError: If the model is not one of the accepted values.
        """
        if self.model not in (("access-om2", "access-om3")):
            raise ValueError(
                f"{self.model} requires to be either " f"access-om2 or access-om3!"
            )

    def run(self) -> None:
        """
        Executes the full experiment workflow:
        - Creates test directories.
        - Ensures model selection.
        - Clones external dependencies.
        - Runs control and perturbation experiments.
        """
        self.create_test_path()
        self.model_selection()
        self.external_tools = ExternalTools(self.yamlfile)

        self.external_tools.clone_om3utils()
        self.external_tools.update_diag_table()

        self.control_experiment = ControlExperiment(self.yamlfile)
        self.control_experiment.manage_experiment()

        self.perturb_experiment = PerturbExperiment(self.yamlfile)
        if self.run_namelists:
            print("==== Start perturbation experiments ====")
            self.perturb_experiment.manage_perturb_expt()
        else:
            print("==== No perturbation experiments are prescribed ====")
