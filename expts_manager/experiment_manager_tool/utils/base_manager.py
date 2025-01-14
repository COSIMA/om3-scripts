import os
from utils.ryaml_handler import read_yaml
from utils import constants

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
        
        self.combo_suffix = constants.COMBO_SUFFIX
        self.branch_perturb = constants.BRANCH_PERTURB
