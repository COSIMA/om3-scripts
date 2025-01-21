#!/usr/bin/env python3
import argparse
from experiment_manager_tool.manager.experiment_manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(
        description="""
        Manage either ACCESS-OM2 or ACCESS-OM3 experiments. 
        Latest version and help: https://github.com/COSIMA/om3-scripts/pull/34
        """
    )

    parser.add_argument(
        "INPUT_YAML",
        type=str,
        nargs="?",
        default="Expts_manager.yaml",
        help="YAML file specifying parameter values for experiment runs. Default is Expts_manager.yaml",
    )

    args = parser.parse_args()
    input_yaml = args.INPUT_YAML
    expt_manager = ExperimentManager(input_yaml)
    expt_manager.run()


if __name__ == "__main__":
    main()
