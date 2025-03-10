"""
YAML Handler for the experiment management.

This module provides utilities for reading and writing YAML files while preserving formatting.
It supports:
- Reading YAML data while keeping quotes intact.
- Writing YAML files with correct formatting.
- Defining a custom `LiteralString` class for multi-line strings.

Functions:
    - `read_yaml`: Reads a YAML file and returns its content as a dictionary.
    - `write_yaml`: Writes a dictionary to a YAML file while preserving formatting.
    - `represent_literal_str`: Handles YAML representation of multi-line strings.
"""

from ruamel.yaml import YAML

ryaml = YAML()
ryaml.preserve_quotes = True


def read_yaml(yaml_path: str) -> dict:
    """
    Reads a YAML file and returns a dictionary.

    Args:
        yaml_path (str): The path to the YAML file.

    Returns:
        dict: Parsed YAML content.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        return ryaml.load(f)


def write_yaml(data: dict, yaml_path: str) -> None:
    """
    Writes a dictionary to a YAML file while preserving formatting.

    Args:
        data (dict): The dictionary containing YAML data.
        yaml_path (str): The path to save the YAML file.
    """
    with open(yaml_path, "w", encoding="utf-8") as f:
        ryaml.dump(data, f)


class LiteralString(str):
    """
    A string subclass that forces YAML to use block literals (|) for multi-line strings.
    """

    pass


def represent_literal_str(dumper, data: LiteralString):
    """
    Represents multi-line strings as block literals (|) in YAML output.

    Args:
        dumper: The YAML dumper.
        data (LiteralString): The string data to represent.

    Returns:
        YAML scalar node using block style (|).
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


ryaml.representer.add_representer(LiteralString, represent_literal_str)
