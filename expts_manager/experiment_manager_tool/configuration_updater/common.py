def update_config_entries(base: dict, change: dict) -> None:
    """
    Recursively update nuopc_runconfig and config.yaml entries.
    """
    for k, v in change.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            update_config_entries(base[k], v)
        else:
            base[k] = v
