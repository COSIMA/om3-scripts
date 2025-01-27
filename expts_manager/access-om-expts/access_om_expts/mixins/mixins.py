"""
Mixins for the experiment management.

This module provides mixin classes for handling:
- Constructing full paths from directory configurations.
- Loading OM3 utilities dynamically.
"""

import os
import sys
import importlib

class FullPathMixin:
    """
    Mixin to construct full paths using `dir_manager`, `test_path`,
    and a specified key from the input YAML file.
    """

    def full_path(self, dir_name_key: str) -> str:
        """
        Constructs the full path using directory settings.

        Args:
            dir_name_key (str): The key corresponds to the directory name in the YAML file.

        Returns:
            str: The constructed full path.

        Raises:
            KeyError: If `dir_name_key` is not found in the input YAML file.
        """
        if dir_name_key not in self.indata:
            raise KeyError(f"{dir_name_key} not found in the input YAML file.")
        return os.path.join(self.dir_manager, self.test_path, self.indata[dir_name_key])


class OM3UtilsLoaderMixin:
    """
    Mixin to dynamically load ACCESS-OM3 utility functions.

    This class ensures `om3utils` is available and correctly loaded when needed.
    """

    _om3_message = False

    def load_om3utils(self, om3utils_path: str) -> None:
        """
        Loads ACCESS-OM3 utility functions from the specified `om3utils_path`.

        Args:
            om3utils_path (str): The path to the `om3utils` package.

        Raises:
            RuntimeError: If the provided path does not exist.
            ImportError: If `om3utils` modules cannot be imported.
        """
        if not os.path.exists(om3utils_path):
            raise RuntimeError(f"om3utils path does not exist: {om3utils_path}")

        if om3utils_path not in sys.path:
            sys.path.append(om3utils_path)

        # import modules from om3-utils
        try:
            nuopc_config = importlib.import_module("om3utils.nuopc_config")
            mom6_config = importlib.import_module("om3utils.MOM6InputParser")

            self.read_nuopc_config = getattr(nuopc_config, "read_nuopc_config")
            self.write_nuopc_config = getattr(nuopc_config, "write_nuopc_config")
            self.mom6_input_parser = mom6_config

        except ModuleNotFoundError as e:
            raise ImportError(f"`om3utils` is not found in {om3utils_path}") from e
        except AttributeError as e:
            raise ImportError("packages are missing in `om3utils`.") from e

    def load_om3utils_if_required(self, model: str) -> None:
        """
        Loads `om3utils` only if the model is `access-om3`.

        Args:
            model (str): The experiment model (e.g., "access-om3").
        """
        if model != "access-om3":
            if not OM3UtilsLoaderMixin._om3_message:
                print(f"-- Skipping om3utils loading for {model}.")
                OM3UtilsLoaderMixin._om3_message = True
            return

        utils_path = self.full_path("utils_dir_name")
        self.load_om3utils(utils_path)
