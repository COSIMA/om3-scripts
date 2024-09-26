# ACCESS-OM Expts Manager
The **ACCESS-OM Experiment Manager** is a Python-based tool designed to streamline the setup and management of either **ACCESS-OM2** or **ACCESS-OM3**. This tool automates the creation of experiment directories, applies parameter changes, and updates relevant configuration files based on user-defined settings in a YAML configuration file.

## Directory Structure
```
.
├── Expts_manager.py
├── write_Expts_manager_yaml.py
├── Expts_manager.yaml
└── README.md

0 directories, 4 files
```

### Components:
1. `Expts_manager.py`:
 - This file contains the `ExptManager` class, which faciliates the setup, configuration, and execution of experiments. Key functionalities include:
    - Configuration management based on user-defined parameters.
    - Automation of directory creation, ensuring a smooth workflow for running experiments.
    - Support for parameter updates, including:
        - MOM6 for **ACCESS-OM3**,
        - Fortran namelists for both **ACCESS-OM2** and **ACCESS-OM3**,
        - Coupling timesteps (`nuopc.runseq`) for **ACCESS-OM3**,
        - Component settings (`nuopc.runconfig`) for **ACCESS-OM3**.

    - Automation of experiment initiation, managing the number of runs to be executed.
    - Ability to skip experiment runs if parameters are identical to those of the control experiment. This functionality can be toggled (currently applicable only to `f90nml`).
    - Prevention of duplicate PBS jobs within the same `test_path` directory.
    - Integration of Git management to track changes during experiments.
    - Updating of experiment metadata, including details and descriptions, facilitated by `Payu`.

2. `Expts_manager.yaml`:
 - This YAML configuration file defines the parameters and settings required for managing control and perturbation experiments. It enables users to:
    - Clone necessary repositories,
    - Setup experiments with customised configurations,
    - Manage utility tools, diagnostic tools, and parameter tuning.

3. `write_Expts_manager_yaml.py`:
 - A Python script used to generate `Expts_manager.yaml`.

## Usage
1. **Edit the YAML File:** Customise experiment parameters and settings by editing `Expts_manager.yaml` or `write_Expts_manager_yaml.py`. Documentation and examples are provided within the file.
   - To generate Expts_manager.yaml, simply run:
     ```
     ./write_Expts_manager_yaml.py
     ```

2. **Run the Manager:** Execute the experiment manager script using the following command:
   ```
   ./Expts_manager.py
   ```

4. **View Available Options:** Users can view available options by:
    ```
    $ ./Expts_manager.py -h
    usage: Expts_manager.py [-h] [INPUT_YAML]
    
    Manage both ACCESS-OM2 and ACCESS-OM3 experiments. Latest version and help: https://github.com/COSIMA/om3-scripts/pull/34
    
    positional arguments:
      INPUT_YAML  YAML file specifying parameter values for expt runs. Default is Expts_manager.yaml
    
    options:
      -h, --help  show this help message and exit
    ```
