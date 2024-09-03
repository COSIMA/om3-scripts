# ACCESS-OM3 Expts Manager
The **ACCESS-OM3 Experiment Manager** is a Python-based tool designed to streamline the setup and management of ACCESS-OM3 experiments. It automates the creation of experiment directories, applies parameter changes, and updates relevant configuration files based on user-defined settings in a YAML configuration file.

## Directory Structure
```
.
├── Expts_manager.py
├── Expts_manager.yaml
└── README.md

0 directories, 3 files
```
### Components:
1. `Expts_manager.py`:
 - contains the `ExptManager` class, which faciliates the setup, configuration, and execution of experiments. Key functionalities include:
    - Handles configuration based on user-defined parameters.
    - Automates the creation of directories and ensures a smooth workflow for running experiments.
    - Supports updates of parameters, including those for MOM6, namelists (`.nml` files) and coupling timestep (`cpl_dt`).
    - Automates the initiation of experiment runs and manages the number of runs to be executed.
    - Skips experiment runs if parameters are identical to the control experiment. This functionality can be switched on and off (currently applicable only to namelists).
    - Integrates Git management during experiments to track changes.
    - Updates experiment metadata, including details and descriptions, facilitated by Payu.

3. `Expts_manager.yaml`:
 - A YAML configuration input file, which is used to define the parameters and settings required for managing control and perturbation experiments. The configuration file enables users to,
    - clone necessary repositories,
    - setup experiments with customised configurations, and,
    - manage diagnostic tools and parameter tunning.

## Usage
1. Edit the YAML File: Customise experiment parameters and settings by editing `Expts_manager.yaml`. Documentation and examples are provided within the file.
2. Run the Manager: Execute the experiment manager script using the command:
   `./Expts_manager.py`

You can view available options using:

```
$ ./Expts_manager.py -h
usage: Expts_manager.py [-h] [INPUT_YAML]

Manage ACCESS-OM3 experiments. Latest version and help: https://github.com/minghangli-uni/Expts_manager

positional arguments:
  INPUT_YAML  YAML file specifying parameter values for expt runs. Default is Expts_manager.yaml

options:
  -h, --help  show this help message and exit
```
