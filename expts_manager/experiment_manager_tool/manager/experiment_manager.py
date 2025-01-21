import os
from experiment_manager_tool.utils.load_external_tools import ExternalTools
from experiment_manager_tool.manager.control_experiment import ControlExperiment
from experiment_manager_tool.manager.perturb_experiment import PerturbExperiment
from experiment_manager_tool.utils.base_manager import BaseManager


class ExperimentManager(BaseManager):
    def __init__(self, yamlfile) -> None:
        super().__init__(yamlfile)
        self.yamlfile = yamlfile
        self.external_tools = None
        self.control_experiment = None
        self.perturb_experiment = None

    def create_test_path(self) -> None:
        """
        Creates the local test directory for blocks of parameter testing.
        """
        if os.path.exists(self.test_path):
            print(f"-- Test directory {self.test_path} already exists!")
        else:
            os.makedirs(self.test_path)
            print(f"-- Test directory {self.test_path} has been created!")

    def model_selection(self) -> None:
        """
        Ensures the model to be either "access-om2" or "access-om3"
        """
        if self.model not in (("access-om2", "access-om3")):
            raise ValueError(
                f"{self.model} requires to be either " f"access-om2 or access-om3!"
            )

    def run(self) -> None:
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
