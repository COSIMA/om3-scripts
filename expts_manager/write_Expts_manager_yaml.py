#!/usr/bin/env python3
try:
    from ruamel.yaml import YAML

    ryaml = YAML()
    ryaml.preserve_quotes = True
    ryaml.indent(mapping=4, sequence=4, offset=2)
except ImportError:
    print("\nFatal error: modules not available.")
    print("On NCI, do the following and try again:")
    print("   module use /g/data/vk83/modules && module load payu/1.1.5\n")
    raise

import os
from io import StringIO


def write_config_yaml_file(file_path, description_sections):
    """
    Writes the YAML file for Experiment Manager tool.

    Parameters:
    - file_path (str): Path to the YAML file to write.
    - description_sections (list of tuples): Each tuple contains a section description (str) and its configs (list of dicts).
    """
    intro_comment = """
# =====================================================================================
# YAML Configuration for Expts_manager.py
# =====================================================================================
# This configuration file defining the parameters and settings required for cloning,
# setting up, and running control and perturbation experiments using `Expts_manager.py`.
# Detailed explanations are provided to ensure the configuration is straightforward.
# =====================================================================================
"""

    def dump_block_style(value):
        buffer = StringIO()
        ryaml.dump(value, buffer)
        buffer.seek(0)
        return buffer.read()

    def write_value(key, value, file, comment=None, indent=0):
        indent_space = " " * (indent * 4)
        if isinstance(value, dict):
            file.write(f"{indent_space}{key}:\n")
            for sub_key, sub_value in value.items():
                write_value(sub_key, sub_value, file, indent=indent + 1)
        elif isinstance(value, list):
            list_content = ", ".join(map(str, value))
            file.write(f"{indent_space}{key}: [{list_content}]")
        else:
            file.write(f"{indent_space}{key}: {value}")
        if comment:
            file.write(f"  {comment}")
        file.write("\n")

    with open(file_path, "w") as file:
        file.write(intro_comment + "\n")
        for description, config_list in description_sections:
            file.write(f"{description}\n")
            for item in config_list:
                if isinstance(item, dict):
                    key = item.get("key", "")
                    value = item.get("value", "")
                    comment = item.get("comment", "")
                    write_value(key, value, file, comment=comment)


if __name__ == "__main__":
    # Descriptions and configs for Model Selection
    descrpt_model_sel = """
# ============ Model Selection ========================================================
"""
    model_sel = [
        {
            "key": "model",
            "value": "access-om3",
            "comment": "# Specify the model to be used. Options: 'access-om2', 'access-om3'",
        },
    ]

    # Descriptions and configs for Utility tool
    descrpt_util = """
# ============ Utility Tool Configuration (only for access-om3) =======================
# The following configuration provides the necessary tools to:
# 1. Parse parameters and comments from `MOM_input` in MOM6.
# 2. Read and write the `nuopc.runconfig` file.
"""
    config_util = [
        {
            "key": "force_overwrite_tools",
            "value": "False",
        },
        {
            "key": "utils_url",
            "value": "git@github.com:minghangli-uni/om3-utils.git",
            "comment": "# Git URL for the utility tool repository",
        },
        {
            "key": "utils_branch_name",
            "value": "main",
            "comment": "# The branch for which the utility tool will be checked out",
        },
        {
            "key": "utils_dir_name",
            "value": "om3-utils",
            "comment": "# Directory name for the utility tool (user-defined)",
        },
    ]

    # Descriptions and configs for Control Experiment Setup
    descrpt_diag = """
# ============ Diagnostic Table (optional) ============================================
# Configuration for customising the diagnostic table.
"""
    config_diag = [
        {
            "key": "diag_url",
            "value": "git@github.com:minghangli-uni/make_diag_table.git",
            "comment": "# Git URL for the `make_diag_table`",
        },
        {
            "key": "diag_branch_name",
            "value": "general_scheme1",
            "comment": "# Branch for the `make_diag_table`",
        },
        {
            "key": "diag_dir_name",
            "value": "make_diag_table",
            "comment": "# Directory name for the `make_diag_table` (user-defined)",
        },
        {
            "key": "diag_ctrl",
            "value": "False",
            "comment": "# Set to 'True' to modify the diagnostic table for the control experiment",
        },
        {
            "key": "diag_pert",
            "value": "False",
            "comment": "# Set to 'True' to modify the diagnostic table for perturbation experiments",
        },
    ]

    # Descriptions and configs for Control Experiment Setup
    descrpt_control = """
# ============ Control Experiment Setup ===============================================
"""
    config_control = [
        {
            "key": "base_url",
            "value": "git@github.com:ACCESS-NRI/access-om3-configs.git",
            "comment": "# Git URL for the control experiment repository",
        },
        {
            "key": "base_commit",
            "value": '"2bc6107"',
            "comment": "# Commit hash to use; Please ensure it is a string!",
        },
        {
            "key": "base_dir_name",
            "value": "Ctrl-1deg_jra55do_ryf",
            "comment": "# Directory name for cloning (user-defined)",
        },
        {
            "key": "base_branch_name",
            "value": "ctrl",
            "comment": "# Branch name for the experiment (user-defined)",
        },
        {
            "key": "test_path",
            "value": "test",
            "comment": "# Relative path for all test (control and perturbation) runs (user-defined)",
        },
    ]

    # Descriptions and configs for Control Experiment Variables
    descrpt_control_expt = """
# ============ Control Experiment Variables ===========================================
# Allows modification of various control experiment settings.
# 1. config.yaml  (access-om2 or access-om3)
# 2. all namelists such as with endswith "_in" or ".nml" etc.  (access-om2 or access-om3)
# 3. cpl_dt (coupling timestep)  (access-om3)
# 4. nuopc.runconfig  (access-om3)
# 5. MOM_input  (access-om3)
# Below are some examples for the illustration purpose, please modify for your own settings.
"""
    config_control_expt = [
        {
            "key": "config.yaml",
            "value": {
                "ncpus": 240,
                "mem": "960GB",
                "walltime": "24:00:00",
                "#jobname": "# `jobname` will be forced to be the name of the directory, which is `Ctrl-1deg_jra55do_ryf` in this example.",
                "metadata": {"enable": True},
                "runlog": True,
                "restart_freq": 1,
            },
        },
        {
            "key": "cpl_dt",
            "value": 1800.0,
            "comment": "# Coupling timestep in the `nuopc_runseq`",
        },
        {
            "key": "nuopc.runconfig",
            "value": {
                "CLOCK_attributes": {
                    "stop_option": "ndays",
                    "stop_n": 1,
                    "restart_option": "ndays",
                    "restart_n": 1,
                },
                "PELAYOUT_attributes": {
                    "atm_ntasks": 24,
                    "cpl_ntasks": 24,
                    "glc_ntasks": 1,
                    "ice_ntasks": 24,
                    "lnd_ntasks": 1,
                    "ocn_ntasks": 216,
                    "ocn_rootpe": 24,
                    "rof_ntasks": 24,
                    "wav_ntasks": 1,
                },
            },
        },
        {
            "key": "ice_in",
            "value": {
                "domain_nml": {
                    "max_blocks": -1,
                    "block_size_x": 15,
                    "block_size_y": 300,
                },
            },
        },
        {
            "key": "input.nml",
            "value": {
                "diag_manager_nml": {
                    "max_axes": 400,
                    "max_files": 200,
                    "max_num_axis_sets": 200,
                },
            },
        },
        {
            "key": "MOM_input",
            "value": {
                "HFREEZE": 12,
                "BOUND_SALINITY": False,
            },
        },
    ]

    # Descriptions and configs for Namelist Tunning
    descrpt_namelists = """
# ============ Namelist Tunning ================================
# Tune parameters across different model components.

# Generalised structure
# 1. Single-parameter tunning within single file
# namelists:
#     filename: (Required).
#         filename_dirs: List of directory names (Optional - user-defined: filename must be appended with "_dirs"; additional strings may follow).
#         groupname: (Required: for f90 namelists or nuopc.runconfig, this is simply the group name; for MOM input, use "MOM_list"; for nuopc.runseq, use "runseq_list").
#             parameter1: list of values
#             parameter2: list of values
#             ...
#     ...

# 2. Multiple-parameter tuning within a single group in a single file
# namelists:
#     filename: (Required).
#         filename_dirs: List of directory names (Optional - user-defined: filename must be appended with "_dirs"; additional strings may follow).
#         groupname_combo: (Required: for f90 namelists or nuopc.runconfig, use the group name; for MOM input, use "MOM_list"; for nuopc.runseq, use "runseq_list", then append "_combo").
#             parameter1: list of values
#             parameter2: list of values
#             ...
#     ...

# 3. Multiple-parameter tuning across different files using user-defined directories
# namelists:
#     cross_block: (Required: additional strings may follow "cross_block").
#         cross_block_dirs: List of directory names (Required - user-defined: filename must be appended with "_dirs"; additional strings may follow).
#         filename:
#             groupname_combo: (Required: for f90 namelists or nuopc.runconfig, use the group name; for MOM input, use "MOM_list"; for nuopc.runseq, use "runseq_list", then append "_combo").
#                 parameter1: list of values
#                 parameter2: list of values
#                 ...
#         filename:
#             groupname_combo: (Required: for f90 namelists or nuopc.runconfig, use the group name; for MOM input, use "MOM_list"; for nuopc.runseq, use "runseq_list", then append "_combo").
#                 parameter1: list of values
#                 parameter2: list of values
#                 ...
#         ...
#
#     cross_block: (Required: may append other strings after "cross_block").
#         cross_block_dirs: list of directory names (Optional - user-defined: filename must be appended with "_dirs", you may append other strings after "_dirs").
#         filename:
#             groupname_combo: (Required: for f90 namelists or nuopc.runconfig, just the group name; for MOM input, "MOM_list", nuopc.runseq, "runseq_list", then append "_combo" at the end).
#                 parameter1: list of values
#                 parameter2: list of values
#                 ...
#         filename:
#             groupname_combo: (Required: for f90 namelists or nuopc.runconfig, just the group name; for MOM input, "MOM_list", nuopc.runseq, "runseq_list", then append "_combo" at the end).
#                 parameter1: list of values
#                 parameter2: list of values
#                 ...
#         ...
#     ...

# The following namelist options are provided as examples.
# Note: Parameters should be based on the underlying physics.
# Some configurations may fail to run or produce invalid results.
# 1.1 Single parameter tuning within a single file using default perturbation directory names.
# 1.2 Single parameter tuning within a single file using user-defined perturbation directory names.
# 2.1 Multi-parameter tuning within a single group in a single file using default perturbation directory names.
# 2.2 Multi-parameter tuning within a single group in a single file using user-defined perturbation directory names.
# 3. Multi-parameter tuning across multiple files.
"""
    config_namelists = [
        {
            "key": "namelists",
            "value": {
                "ice_in": {
                    "ponds_nml": {
                        "dpscale": [0.002, 0.003],
                        "rfracmax": [1.1, 1.2],
                    },
                    "ice_in_dirs_test": ["icet1", "icet2", "icet3", "icet4"],
                    "shortwave_nml": {
                        "ahmax": [0.2, 0.3],
                        "r_snw": [0.1, 0.2],
                    },
                },
                "MOM_input": {
                    "MOM_list4": {
                        "MINIMUM_DEPTH": [0, 0.5],
                        "MAXIMUM_DEPTH": [6000.0, 7000.0, 8000.0],
                    },
                    "MOM_input_dirs1": ["lexpt0", "lexpt1"],
                    "MOM_list1_combo": {
                        "DT_THERM": [3600.0, 108000.0],
                        "DIABATIC_FIRST": [False, False],
                        "THERMO_SPANS_COUPLING": [True, True],
                    },
                },
                "cross_block2": {
                    "cross_block2_dirs": ["cg_1", "cg_2"],
                    "nuopc.runconfig": {
                        "CLOCK_attributes_combo": {
                            "restart_n": [1, 1],
                            "restart_option": ["ndays", "ndays"],
                            "stop_n": [1, 1],
                            "stop_option": ["ndays", "ndays"],
                            "ocn_cpl_dt": [1800.0, 7200.0],
                        },
                        "PELAYOUT_attributes_combo": {
                            "ocn_ntasks": [168, 120],
                        },
                    },
                    "config.yaml": {
                        "config_list1_combo": {
                            "ncpus": [192, 144],
                            "mem": ["768GB", "576GB"],
                        },
                    },
                    "ice_in": {
                        "shortwave_nml_combo": {
                            "albicei": [0.36, 0.39],
                            "albicev": [0.78, 0.81],
                        },
                        "ponds_nml_combo": {
                            "dpscale": [0.002, 0.003],
                        },
                    },
                    "MOM_input": {
                        "MOM_list1_combo": {
                            "DT_THERM": [3600.0, 7200.0],
                            "DIABATIC_FIRST": [False, False],
                            "THERMO_SPANS_COUPLING": [True, True],
                            "DTBT_RESET_PERIOD": [3600.0, 7200.0],
                        },
                    },
                    "nuopc.runseq": {
                        "runseq_list1_combo": {
                            "cpl_dt": [1800.0, 7200.0],
                        },
                    },
                },
            },
        },
    ]

    # Descriptions and configs for Perturbation Experiment Setup (Optional)
    descrpt_perturb_setup = """
# ============ Perturbation Experiment Setup (Optional - access-om3) =======================
# Configure settings for perturbation experiments. Currently, only `nuopc.runconfig` is supported.
# If conducting parameter tuning for `nuopc.runconfig`, any pre-existing settings in this section 
# will be purged by the above namelist tunning.
"""
    config_perturb_setup = [
        {
            "key": "perturb_run_config",
            "value": {
                "CLOCK_attributes": {
                    "stop_option": "nyears",
                    "stop_n": 1,
                    "restart_option": "nyears",
                    "restart_n": 1,
                },
            },
        },
    ]

    descrpt_runs = """
# ============ Control experiment and perturbation Runs ===================================
# This section configures the settings for running control experiments and their corresponding perturbation tests.
    """
    config_runs = [
        {
            "key": "ctrl_nruns",
            "value": 0,
            "comment": "\n# Number of control experiment runs.\
            \n# Default: 0.\
            \n# Adjust this value to set the number of iterations for the control experiment, which serves as the baseline for perturbations.\n",
        },
        {
            "key": "run_namelists",
            "value": True,
            "comment": "\n# Determines whether to run using the specified namelists.\
            \n# Default: False.\
            \n# Set to 'True' to apply configurations from the namelist section; otherwise, 'False' to skip this step.\n",
        },
        {
            "key": "check_duplicate_jobs",
            "value": True,
            "comment": "\n# Checks if there are duplicate PBS jobs within the same parent directory (`test_path`) based on their names.\
            \n# This check is useful when you have existing running jobs and want to add additional tests, which helps avoid conflicts by ensuring new jobs don't duplicate existing ones in the same `test_path`.\
            \n# The check will not be triggered if the jobs are located in different `test_path`. It only applies to jobs within the same `test_path` directory.\
            \n# Default: True.\
            \n# If duplicates are found, a message will be printed indicating the presence of duplicate runs and those runs will be skipped.\n",
        },
        {
            "key": "check_skipping",
            "value": False,
            "comment": "\n# Checks if certain runs should be skipped based on pre-existing conditions or results. Currently only valid for nml type.\
            \n# Default: False.\
            \n# Set to 'True' if you want the system to skip runs under specific criteria; otherwise, keep it 'False'. Currently only valid for nml type.\n",
        },
        {
            "key": "force_restart",
            "value": False,
            "comment": "\n# Controls whether to force a restart of the experiments regardless of existing initial conditions.\
            \n# Default: False.\
            \n# Set to 'True' to enforce a restart of the control and perturbation runs.\n",
        },
        {
            "key": "startfrom",
            "value": "'rest'",
            "comment": "\n# Defines the starting point for perturbation tests.\
            \n# Options: a specific restart number of the control experiment, or 'rest' to start from the initial state.\
            \n# This parameter determines the initial condition for each perturbation test.\n",
        },
        {
            "key": "nruns",
            "value": 0,
            "comment": "\n# Total number of output directories to generate for each Expts_manager member.\
            \n# Default: 0.\
            \n# Specifies how many runs of each perturbation experiment will be started; this number correlates with the different parameter combinations defined in the configuration.",
        },
    ]

    yaml_file_path = os.path.join(os.getcwd(), "Expts_manager.yaml")

    write_config_yaml_file(
        yaml_file_path,
        [
            (descrpt_model_sel, model_sel),
            (descrpt_util, config_util),
            (descrpt_diag, config_diag),
            (descrpt_control, config_control),
            (descrpt_control_expt, config_control_expt),
            (descrpt_namelists, config_namelists),
            (descrpt_perturb_setup, config_perturb_setup),
            (descrpt_runs, config_runs),
        ],
    )
