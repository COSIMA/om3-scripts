import os
import sys


def detect_HPC() -> str:
    """
    Detects the current HPC system.

    Returns:
        str: The detected HPC identifier (e.g., 'gadi', 'setonix')
    """
    try:
        nodename = os.uname().nodename
        return nodename.split(".")[1].lower()
    except IndexError:
        raise RuntimeError("Failed to detect HPC system...")


def load_payu() -> None:
    """
    Loads the PAYU managing tool.

    - Detects the current HPC system.
    - Checks if PAYU is already loaded to prevent redundant restarts.
    - Loads the PAYU module and sets up the correct runtime environment.
    """
    if os.getenv("PAYU_ENV") == "loaded":
        print("PAYU is already loaded. Skipping restart.")
        return

    hpc_name = detect_HPC()

    if hpc_name == "gadi":
        # Currently manually sets the main.py, could be improved.
        module_name = "experiment_manager_tool.main"

        # Preserves the optional yaml input file.
        new_args = " ".join(sys.argv[1:])
        if new_args:
            print(f"Overrided input yaml file: `{new_args}` located at {os.getcwd()}")
        else:
            print(
                f"Default input yaml file: `Expts_manager.yaml` located at {os.getcwd()}"
            )

        # Sets PAYU_ENV
        os.environ["PAYU_ENV"] = "loaded"

        # Loads Payu inside the correct environment
        command = (
            f"source /etc/profile && "
            f"module use /g/data/vk83/prerelease/modules && "
            f"module load payu/dev && "
            f"export PAYU_ENV=loaded && "
            f"python3 -m {module_name} {new_args}"
        )
        os.execve("/bin/bash", ["/bin/bash", "-c", command], os.environ)

    elif hpc_name == "setonix":
        raise NotImplementedError("Payu support for Setonix is not yet implemented.")
    else:
        raise ValueError(f"Unsupported HPC system: {hpc_name}. Payu cannot be loaded.")


# load PAYU
load_payu()
