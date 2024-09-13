#!/usr/bin/env python3
try:
    from ruamel.yaml import YAML

    ryaml = YAML()
    ryaml.preserve_quotes = True
except ImportError:
    print("\nFatal error: modules not available.")
    print("On NCI, do the following and try again:")
    print("   module use /g/data/vk83/modules && module load payu/1.1.5\n")
    raise

ryaml.indent(mapping=4, sequence=4, offset=2)
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
# ===========================================================
# YAML config for Expts_manager.py
# ===========================================================
# This config file contains the necessary parameters and configs
# to clone, setup, and run control experiments and perturbation tests using `Expts_manager.py`. 
# Detailed explanations are provided to ensure clarity and ease of use for prospective users.
# ===========================================================
"""

    def dump_block_style(value):
        buffer = StringIO()
        ryaml.dump(value, buffer)
        buffer.seek(0)
        return buffer.read()

    with open(file_path, "w") as file:
        file.write(intro_comment + "\n")
        for description, config_list in description_sections:
            file.write(description + "\n")
            for item in config_list:
                if isinstance(item, dict):
                    key = item.get("key", "")
                    value = item.get("value", "")
                    comment = item.get("comment", "")
                    if isinstance(value, dict):
                        content = dump_block_style(value)
                        content = "\n".join(
                            " " * 4 + line for line in content.splitlines()
                        )
                        file.write(f"{key}:\n{content}\n")
                    else:
                        if comment:
                            file.write(f"{key}: {value}   {comment}\n")
                        else:
                            file.write(f"{key}: {value}\n")
                else:
                    file.write(f"{item}\n")


if __name__ == "__main__":
    # Descriptions and configs for Utility tool
    descrpt_util = """
# ============ Utility Tool config =======================
# Provides tools for:
# 1. Parsing parameters and comments from `MOM_input` in MOM6.
# 2. Reading and writing the `nuopc.runconfig` file.
"""
    config_util = [
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
# ============ diagnostic table (optional) =======================
# Configuration for modifying the diagnostic table.
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
            "comment": "# Modify diag_table for control experiment if true",
        },
        {
            "key": "diag_pert",
            "value": "False",
            "comment": "# Modify diag_table for perturbation experiments if true",
        },
    ]

    # Descriptions and configs for Control Experiment Setup
    descrpt_control = """
# ============ Control Experiment Setup =======================
# config for setting up control experiments.
"""
    config_control = [
        {
            "key": "base_url",
            "value": "git@github.com:ACCESS-NRI/access-om3-configs.git",
            "comment": "# Git URL for the control experiment repository",
        },
        {
            "key": "base_commit",
            "value": "2bc6107",
            "comment": "# Commit hash to use",
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
            "comment": "# Path for all test runs",
        },
    ]

    # Descriptions and configs for Control Experiment Variables
    descrpt_control_expt = """
# ============ Control Experiment Variables =======================
# Allows modification of various control experiment settings.
# 1. config.yaml
# 2. cpl_dt (coupling timestep)
# 3. nuopc.runconfig
# 4. all namelists such as ice_in, input.nml etc
# 5. MOM_input
# Below are some examples for the illustration purpose.
"""
    config_control_expt = [
        {
            "key": "config.yaml",
            "value": {
                "ncpus": 240,
                "mem": "960GB",
                "walltime": "24:00:00",
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
                    "block_size_y": 20,
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
    # Descriptions and configs for Perturbation Experiment Setup (Optional)
    descrpt_perturb_setup = """
# ============ Perturbation Experiment Setup (Optional) =======================
# Configure perturbation experiments, currently supports `nuopc.runconfig` only.
"""
    config_perturb_setup = [
        {
            "key": "perturb_run_config",
            "value": {
                "CLOCK_attributes": {
                    "stop_option": "ndays",
                    "stop_n": 1,
                    "restart_option": "ndays",
                    "restart_n": 1,
                },
            },
        },
    ]

    # Descriptions and configs for Namelist Tunning
    descrpt_namelists = """
# ============ Namelist Tunning ================================
# Allows fine-tuning of various parameters across different model components 
# such as ice_in, input.nml, drv_in, and MOM_input.

# Generlised structure
# namelists
#     parameter_block1:
#         parameter_group1:
#             parameter1: list of string(s) or value(s)
#             parameter2: list of string(s) or value(s)
#             ...
#         parameter_group2_combo:
#             parameter1: list of string(s) or value(s)
#             parameter2: list of string(s) or value(s)
#             ...
#         parameter_group3_xxx: list of user-defined perturbation experiment directory names
#         parameter_group3:
#             parameter1: list of string(s) or value(s)
#             parameter2: list of string(s) or value(s)
#             ...
#         parameter_group4_xxx: list of user-defined perturbation experiment directory names
#         parameter_group4_combo:
#             parameter1: list of string(s) or value(s)
#             parameter2: list of string(s) or value(s)
#             ...

# There are three types of parameters available for tunning, 
# 1. namelists (nml), 
# 2. parameters in MOM_input (mom6), and 
# 3. coupling timestep in nuopc.runseq (cpl_dt).

# 1. nml type:
# (1) Individual parameter tunning:
#    parameter_block (filename, e.g., ice_in)
#        parameter_group (namelist, e.g., shortwave_nml)
#            parameter1: list1 (tunning parameter: tunning values, e.g., ahmax: [0.2, 0.3])
#            parameter2: list2 (tunning parameter: tunning values, e.g., r_snw: [0.1, 0.2])
# In the above example, there will be 4 individual perturbation experiments generated.
#
# (2) Combined parameters tunning:
# For combined parameters tunning, `parameter_group` requires to suffix with `_combo`, e.g., `shortwave_nml_combo`
#    parameter_block (filename, e.g., ice_in)
#        parameter_group (namelist, e.g., shortwave_nml_combo)
#            parameter1: list1 (tunning parameter: tunning values, e.g., albicei: [ 0.36, 0.39 ])
#            parameter2: list2 (tunning parameter: tunning values, e.g., albicev: [ 0.78, 0.81 ])
# In the above example, there will be 2 perturbation experiments generated, where each column will form an experiment.
# 
# Perturbation experiment directory names:
# The perturbation experiment directory names of the above (1) and (2) will be named as `parameter1_value1_parameter2_value2...`.
# For example, for (1), the created experiment directory names will be, ahmax_0.2, ahmax_0.3, r_snw_0.1, r_snw_0.2
#              for (2), the created experiment directory names will be, albicei_0.36_albicev_0.78, albicei_0.39_albicev_0.81
#
# (3) User-defined perturbation experiment directory names [optional] with (1) or (2):
# Current tool also provides an [optional] user-defined experiment directory names, which must be positioned on top of the `parameter_group` and start with the string of the filename.
# The number of user-defined directory names must have the same length of the parameters. 
# Below is an example with (1),
#    filename+xxx: list of strings (e.g., ice_in_dir_test: ['test_a', 'test_10', 'test_ds', 'test_fdis'])
#    parameter_block (filename, e.g., ice_in)
#        parameter_group (namelist, e.g., shortwave_nml)
#            parameter1: list1 (tunning parameter: tunning values, e.g., ahmax: [0.2, 0.3])
#            parameter2: list2 (tunning parameter: tunning values, e.g., r_snw: [0.1, 0.2])
# In the above example, there will be 4 individual perturbation experiments generated and are named as, test_a, test_10, test_ds, test_fdis.
#
# Similarly for (2),
#    filename+xxx: list of strings (e.g., ice_in_0: ['abc_1', 'mk_100'])
#    parameter_block (filename, e.g., ice_in)
#        parameter_group (namelist, e.g., shortwave_nml_combo)
#            parameter1: list1 (tunning parameter: tunning values, e.g., albicei: [ 0.36, 0.39 ])
#            parameter2: list2 (tunning parameter: tunning values, e.g., albicev: [ 0.78, 0.81 ])
# In the above example, there will be 2 perturbation experiments generated and are named as, abc_1, mk_100.
# 
# 2. mom6 type:
# Similar to the `nml` type, parameter block is the filename, hence is `MOM_input`.
# The string of `parameter_group` of mom6 type is fixed and always start with `MOM_list`.
#
# (4) Individual parameter tunning:
#    parameter_block (filename, e.g., MOM_input)
#        parameter_group (namelist, e.g., MOM_list_test)
#            parameter1: list1 (tunning parameter: tunning values, e.g., HFREEZE: [14, 16])
# In the above example, there will be 2 individual perturbation experiments generated are name as HFREEZE_14, HFREEZE_16.
#
# (5) Combined parameters tunning:
#    parameter_block (filename, e.g., MOM_input)
#        parameter_group (namelist, e.g., MOM_list_1_combo)
#            parameter1: list1 (tunning parameter: tunning values, e.g., DT_THERM: [3600.0 ,108000.0])
#            parameter2: list2 (tunning parameter: tunning values, e.g., DIABATIC_FIRST:[True   , False])
# In the above example, there will be 2 individual perturbation experiments generated are name as DT_THERM_3600_DIABATIC_FIRST_True, DT_THERM_108000_DIABATIC_FIRST_False.
#
# (6) User-defined perturbation experiment directory names [optional] with (4) or (5):
#    filename+xxx: list of strings (e.g., MOM_input_dir_test1: ['test_b', 'test_20'])
#    parameter_block (filename, e.g., MOM_input)
#        parameter_group (namelist, e.g., MOM_list_test)
#            parameter1: list1 (tunning parameter: tunning values, e.g., HFREEZE: [14, 16])
# In the above example, there will be 2 individual perturbation experiments generated are name as test_b, test_20.
#
#    filename+xxx: list of strings (e.g., MOM_input_dir_test2: ['test_c', 'test_30'])
#    parameter_block (filename, e.g., MOM_input)
#        parameter_group (namelist, e.g., MOM_list_1_combo)
#            parameter1: list1 (tunning parameter: tunning values, e.g., DT_THERM: [3600.0 ,108000.0])
#            parameter2: list2 (tunning parameter: tunning values, e.g., DIABATIC_FIRST:[True   , False])
# In the above example, there will be 2 individual perturbation experiments generated are name as test_c, test_30.
#
# 3. cpl_dt type:
# Similar to the above two types, the only differences are: 
# the [optional] perturbation experiment directory names shall start with `runseq`, and
# the string of `parameter_group` of cpl_dt type is fixed and always start with `runseq_list`.

# The following namelist options are provided for demonstration purposes.
# Please note that parameters should be determined by the underlying physics of the model.
# So, some configurations may not run successfully or produce valid results.
"""
    config_namelists = [
        {
            "key": "namelists",
            "value": {
                "ice_in": {
                    "shortwave_nml_combo": {
                        "albicei": [0.36, 0.39, 0.47],
                        "albicev": [0.78, 0.81, 0.90],
                    },
                    "ice_in_dir": ["icet1", "icet2", "icet3", "icet4"],
                    "shortwave_nml": {
                        "ahmax": [0.2, 0.3],
                        "r_snw": [0.1, 0.2],
                    },
                    "ice_in_test": ["cice_mu_ta", "cice_mu_taa", "cice_ta_mu"],
                    "dynamics_nml_combo": {
                        "mu_rdg": [2, 3, 4],
                        "turning_angle": [0, 1, 2],
                    },
                    "thermo_nml": {
                        "chio": [0.001],
                    },
                },
                "input.nml": {
                    "diag_manager_nml_combo": {
                        "max_axes": [450],
                        "max_files": [250],
                        "max_num_axis_sets": [250],
                    },
                },
                "drv_in": {
                    "debug_inparm_nml": {"create_esmf_pet_files": [".true."]},
                },
                "MOM_input": {
                    "MOM_input_dir1": ["lexpt0", "lexpt1"],
                    "MOM_list1_combo": {
                        "DT_THERM": [3600.0, 108000.0],
                        "DIABATIC_FIRST": [True, False],
                    },
                    "MOM_input_dir2": ["expt5"],
                    "MOM_list2": {"THICKNESSDIFFUSE": [False]},
                    "MOM_list3": {"HFREEZE": [12, 14]},
                    "MOM_input_dir10": [
                        "min_depth0",
                        "min_depth0_5",
                        "max_depth_6000m",
                        "max_depth_7000m",
                    ],
                    "MOM_list4": {
                        "MINIMUM_DEPTH": [0, 0.5],
                        "MAXIMUM_DEPTH": [6000.0, 7000.0],
                    },
                    "MOM_input_dir25": ["timestep_therm_test"],
                    "MOM_list5_combo": {
                        "DT_THERM": [900.0],
                        "DIABATIC_FIRST": [False],
                        "THERMO_SPANS_COUPLING": [True],
                    },
                },
                "nuopc.runseq": {
                    "runseq_expt_dir1": ["cpl_dt1", "cpl_dt2"],
                    "runseq_list1": {
                        "cpl_dt": [1800.0, 3600.0],
                    },
                },
            },
        }
    ]

    descrpt_runs = """
# ============ Control experiment and perturbation Runs ===================================
# This section configures the settings for running control experiments and their corresponding perturbation tests.
# Key parameters include the number of runs, restart options, and directory management for output.
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
            \n# This check is useful when you have existing running jobs and want to add additional tests, which helps avoid conflicts by ensuring new jobs dont duplicate exisiting ones in the same `test_path`.\
            \n# The check will not be triggered if the jobs are located in different `test_path`. It only applies to jobs within the same `test_path` directory.\
            \n# Default: True.\
            \n# If duplicates are found, a message will be printed indicating the presence of duplicate runs and those runs will be skipped.\n",
        },
        {
            "key": "check_skipping",
            "value": False,
            "comment": "\n# Checks if certain runs should be skipped based on pre-existing conditions or results. Currently only valids to nml type.\
            \n# Default: False.\
            \n# Set to 'True' if you want the system to skip runs under specific criteria; otherwise, keep it 'False'. Currently only valids to nml type.\n",
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
            (descrpt_util, config_util),
            (descrpt_diag, config_diag),
            (descrpt_control, config_control),
            (descrpt_control_expt, config_control_expt),
            (descrpt_perturb_setup, config_perturb_setup),
            (descrpt_namelists, config_namelists),
            (descrpt_runs, config_runs),
        ],
    )
