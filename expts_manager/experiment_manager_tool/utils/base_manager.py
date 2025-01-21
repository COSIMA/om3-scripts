import os
from experiment_manager_tool.utils.ryaml_handler import read_yaml


class BaseManager:
    """
    Initialises shared attributes
    """

    def __init__(self, yamlfile: str) -> None:
        self.yamlfile = yamlfile
        self.dir_manager = os.getcwd()
        self._load_variables(self.yamlfile)

    def _load_variables(self, yamlfile: str) -> None:
        self.indata = read_yaml(yamlfile)
        self.dir_manager = os.getcwd()
        self.test_path = self.indata.get("test_path")
        self.model = self.indata.get("model")
        self.run_namelists = self.indata.get("run_namelists", False)

        self.branch_perturb = "perturb"
