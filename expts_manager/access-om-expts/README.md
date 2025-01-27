# access-om-expts: Experiment Manager for ACCESS-OM2/OM3

**access-om-expts** is a Python-based tool designed to streamline the setup and management of `ACCESS-OM2` and `ACCESS-OM3` experiments. It automates parameter modifications and updates relevant configuration files based on user-defined settings in a YAML configuration file.

## Key features

- **Automated experiment setup** for control and perturbation runs.
- **Dynamic configuration updates** (e.g., `config.yaml`, `MOM_input`, `nuopc.runconfig`, `ice_in` and etc).
- **PBS job manager** for submitting and monitoring jobs.
- **Modular design** with YAML-based parameter tuning.
- **Integration with `payu`** for experiment management.

## Installation & Setup

To install `access-om-expts`, simply clone the repository and install it via `pip`.  
- No additional dependencies need to be installed, but you must load the latest [`payu`](https://github.com/payu-org/payu) before running the tool.

### **1. Clone the repository**
```bash
$ git clone https://github.com/COSIMA/om3-scripts.git
$ cd om3-scripts/access-om-expts
```

### **2. Load required modules** (currently on Gadi only)
```bash
$ module use /g/data/vk83/modules && module load payu/1.1.6
```

### **3. Install the package**

Install locally:
```bash
$ python3 -m pip install --user .
```
Or install in a virtual environment:
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install .
```

### **4. Usage**

Once installed, `access-om-expts` can be used to manage `ACCESS-OM2` or `ACCESS-OM3` experiments as follows:
```bash
$ access-om-expts [Expts_manager.yaml]
```
where, `Expts_manager.yaml` is the default name for the input YAML configuration file.
- If using the default file name, you can omit the input argument,
```bash
$ access-om-expts
```
- Otherwise, specify the name of your custom YAML configuration file,
```bash
$ access-om-expts custom_experiment.yaml
```
### **5. Available options**

To view the available commands and options,
```bash
$ access-om-expts -h

usage: access-om-expts [-h] [INPUT_YAML]

Manage both ACCESS-OM2 and ACCESS-OM3 experiments.
Latest version and help: https://github.com/COSIMA/om3-scripts

positional arguments:
  INPUT_YAML   YAML file specifying parameter values for experiment runs. Default is Expts_manager.yaml

options:
  -h, --help   Show this help message and exit
```

## Input YAML configuration

Experiments are configured via a YAML file (e.g., `Expts_manager.yaml`). Modify this file or create a customised one to specify experiment parameters, namelists, and configurations.

A detailed example YAML template is included in the repository for reference.

## Repository management

`access-om-expts` will download and manage additional repositories as specified in the input YAML configuration file (e.g., `Expts_manager.yaml`),
- [Optional] [`make_diag_table`](https://github.com/COSIMA/make_diag_table) -> Generates `diag_table` for user-defined diagnostics.
- [Required for `ACCESS-OM3`] [`om3-utils`](https://github.com/minghangli-uni/om3-utils) -> Provides additional utilities for configuring `ACCESS-OM3`.

