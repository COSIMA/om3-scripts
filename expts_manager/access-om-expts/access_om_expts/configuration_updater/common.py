"""
Utility functions for updating config.yaml and nuopc_runconfig.

This module provides helper functions for recursively updating
entries in `nuopc_runconfig` and `config.yaml`.
"""


def update_config_entries(base: dict, change: dict) -> None:
    """
    Recursively update nuopc_runconfig and config.yaml entries.

    Args:
        base (dict): The base configuration dictionary to be updated.
        change (dict): The dictionary containing new or modified values.
    """

    for k, v in change.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            update_config_entries(base[k], v)
        else:
            base[k] = v
