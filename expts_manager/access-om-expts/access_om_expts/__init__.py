"""
This module initialises the environment for the experiment manager tool.

It provides functionality to verify the presence and compatibility of
`payu` in different HPC environments, e.g., Gadi, Setonix

NOTE: Setonix support is not available currently. However, the tool 
remains functional and should work as expected when Setonix becomes operational.

Methods:
    detect_hpc() -> str
    check_is_payu_loaded() -> bool
    supports_clone_s() -> bool
    ensure_payu() -> None

The `ensure_payu()` method should be called at the start to enforce that
`payu` is properly loaded or installed based on the current environment.
"""

import os
import subprocess
import re
import importlib.util


def detect_hpc() -> str:
    """
    Detects the current HPC environment.

    Returns:
        str: The detected HPC identifier (e.g., 'gadi', 'setonix').

    Raises:
        RuntimeError: If the HPC environment cannot be determined.
    """
    try:
        hostname_tmp = os.uname().nodename.split(".")
        if len(hostname_tmp) < 2:
            raise ValueError(
                "Hostname format is unexpected. "
                "Hence unable to determine HPC environment."
            )

        hpc_name = hostname_tmp[1].lower()
        return hpc_name
    except Exception as e:
        raise RuntimeError(f"Failed to detect HPC environment: {e}") from e


def check_is_payu_loaded() -> bool:
    """
    Checks if `payu` is loaded in the current environment.

    Returns:
        bool: True if `payu` is available, False otherwise.
    """
    return importlib.util.find_spec("payu") is not None


def supports_clone_s() -> bool:
    """
    Checks if the `payu clone --start-point` command is supported.
    This allows cloning experiments directly from a specific commit or tag,
    without requiring an explicit branch.

    Returns:
        bool: True if supported, False otherwise.
    """
    try:
        res = subprocess.run(
            ["payu", "clone", "--help"], stdout=subprocess.PIPE, text=True, check=True
        )
        tmp_txt = res.stdout.lower()

        match = re.search(r"(\s|^)--start-point\b", tmp_txt)
        return bool(match)
    except subprocess.CalledProcessError:
        return False


def ensure_payu() -> None:
    """
    Ensures that a proper `payu` is available based on the current environment.
    If any conditions are not met, a `RuntimeError` is raised with
    appropriate instructions for resolving the issue.

    Raises:
        RuntimeError: If `payu` is not loaded or does not support the required features.
    """
    try:
        hpc_name = detect_hpc()
        print(f"-- Detected HPC environment: {hpc_name}")
    except RuntimeError as e:
        print(f"Error: {e}")

    if not check_is_payu_loaded():
        raise RuntimeError(
            "The latest `payu` is required but not loaded. "
            "Please load it using your environment module system, "
            "e.g., 'module use module use /g/data/vk83/modules && "
            "module load payu/1.1.6', then install by "
            "`python3 -m pip install --user .`"
        )
    if not supports_clone_s():
        raise RuntimeError(
            "`payu` is loaded, "
            "but it does not support the `payu clone --start-point` command. "
            "Please ensure you have the latest version of `payu` loaded."
        )


# load payu
ensure_payu()
