"""
Copyright 2025 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
SPDX-License-Identifier: Apache-2.0

=========================================================================================
ACCESS-OM-Expts: Experiment Manager for ACCESS-OM2/OM3
=========================================================================================

This script manages ACCESS-OM2 and ACCESS-OM3 experiments, automating the setup,
configuration, and execution of control and perturbation runs. It facilitates:
  - Experiment management.
  - Dynamic configuration updates (`config.yaml`, `MOM_input`, `nuopc.runconfig`, `ice_in`, etc.).
  - PBS job submission and monitoring.
  - Automated repository management for required utilities.

To run:
```
  $ access-om-expts [Expts_manager.yaml]
```
where `Expts_manager.yaml` is the default YAML input file defining the experiment setup.
If omitted, the script will default to `Expts_manager.yaml`. Users can specify a custom
YAML configuration file if needed.

Dependencies:
  - This script requires `payu`, which must be loaded via the following modules:
    ```
    module use /g/data/vk83/modules && module load payu/1.1.6
    ```
  - No additional dependencies need to be installed manually.

Additional Repository Management:
  - The script automatically downloads and manages additional repositories during execution:
    - [`om3-utils`](https://github.com/minghangli-uni/om3-utils) (required for ACCESS-OM3).
    - [`make_diag_table`](https://github.com/COSIMA/make_diag_table) (optional).

Contact:
    Minghang Li <Minghang.Li1@anu.edu.au>
=========================================================================================
"""

import argparse
from access_om_expts.manager.experiment_manager import ExperimentManager


def main() -> None:
    """
    Managing ACCESS-OM2 or ACCESS-OM3 experiments.

    Example usage:
        python3 -m access_om_expts.main [Expts_manager.yaml]

    Args:
        INPUT_YAML_FILE (str, optional):
            Path to the YAML file specifying parameter values for experiment runs.
            Defaults to "Expts_manager.yaml".
    """
    parser = argparse.ArgumentParser(
        description="""
        Manage ACCESS-OM2 or ACCESS-OM3 experiments.
        Latest version and help: https://github.com/COSIMA/om3-scripts/access-om-expts
        """
    )

    parser.add_argument(
        "INPUT_YAML_FILE",
        type=str,
        nargs="?",
        default="Expts_manager.yaml",
        help="YAML file specifying parameter values for experiment runs."
        "Default is Expts_manager.yaml",
    )

    args = parser.parse_args()
    input_yaml = args.INPUT_YAML_FILE
    expt_manager = ExperimentManager(input_yaml)
    expt_manager.run()


if __name__ == "__main__":
    main()
