import os
import sys

class FullPathMixin:
    def full_path(self, dir_name_key: str) -> str:
        """
        Constructs the full path based on dir_manager, test_path, and an input parameter in the YAML file.
        """
        if dir_name_key not in self.indata:
            raise KeyError(f"{dir_name_key} not found in the input YAML file.")
        return os.path.join(self.dir_manager, self.test_path, self.indata[dir_name_key])

class OM3UtilsLoaderMixin:
    _om3_message = False

    def load_om3utils(self, om3utils_path: str) -> None:
        if not os.path.exists(om3utils_path):
            raise RuntimeError("om3utils path does not exist: {om3utils_path}")

        if om3utils_path not in sys.path:
            sys.path.append(om3utils_path)

        # load modules from om3-utils
        try:
            from om3utils import MOM6InputParser
            from om3utils.nuopc_config import read_nuopc_config, write_nuopc_config
            self.read_nuopc_config = read_nuopc_config
            self.write_nuopc_config = write_nuopc_config
            self.MOM6InputParser = MOM6InputParser

        except ImportError as e:
            raise ImportError(f"Failed to import modules from om3-utils") from e

    def load_om3utils_if_required(self, model: str) -> None:
        if model != "access-om3":
            if not OM3UtilsLoaderMixin._om3_message:
                print(f"-- Skipping om3utils loading for {model}.")
                OM3UtilsLoaderMixin._om3_message = True
            return

        utils_path = self.full_path("utils_dir_name")
        self.load_om3utils(utils_path)