"""
Perturbation Experiment Manager for the experiment management.

This module handles perturbation experiments, including:
- Managing and setting up experiment directories.
- Updating configuration files (e.g., `config.yaml`, `MOM_input`, `nuopc.runconfig`).
- Running perturbation experiments using PBS job submission.
"""

import os
import warnings
import subprocess
from access_om_expts.utils.util_functions import update_diag_table
from access_om_expts.utils.metadata import MetaData
from access_om_expts.configuration_updater.mom6_updater import MOM6Updater
from access_om_expts.manager.control_experiment import ControlExperiment
from access_om_expts.pbs_job_manager.pbs_job_manager import PBSJobManager
from access_om_expts.manager import PERTURB_BRANCH_NAME, BLOCK_NAME


class PerturbExperiment(ControlExperiment):
    """
    Manages the setup and execution of perturbation experiments.

    This class:
    - Creates experiment directories.
    - Updates configuration files.
    - Runs perturbation experiments.

    Attributes:
        expt_names (list): List of experiment names.
        num_expts (int): Number of experiments.
        tmp_count (int): Counter for tracking processed groups.
        group_count (int): Number of parameter groups.
        commt_dict_change (dict): Dictionary of MOM6 comments.
        list_of_param_dict_change (list): List of all parameter changes.
        list_of_groupname (list): List of f90nml group names.
        diag_pert (bool): Whether to update the diagnostic table.
        diag_path (str): Path to the diagnostic table directory.
        mom6updater (MOM6Updater): MOM6 updater instance.
        metadata (MetaData): Metadata manager.
        pbsjobmanager (PBSJobManager): PBS job manager instance.

    Methods:
        - `manage_perturb_expt`: Main function to setup perturbation experiments.
        - `_process_namelist_block`: Processes individual parameter blocks.
        - `_process_params_cross_files`: Processes cross-file parameters.
        - `_generate_combined_dicts`: Handles nested parameters across experiments.
        - `_preprocess_nested_dicts`: Preprocesses nested dictionary structures.
        - `_handle_nested_dict`: Handles recursive nested dictionary structures.
        - `setup_expts`: Sets up and configures experiments.
    """

    def __init__(self, yamlfile: str) -> None:
        """
        Initialises the PerturbExperiment manager.

        Args:
            yamlfile (str): Path to the YAML configuration file.
        """
        super().__init__(yamlfile)

        # experiment setup
        self.expt_names = None
        self.num_expts = None
        self.tmp_count = 0
        self.group_count = None

        # Parameter-related initialisation
        self.commt_dict_change = {}  # MOM6 comment
        self.list_of_param_dict_change = []  # ALL parameter changes
        self.list_of_groupname = []  # f90nml group names (not the actual parameters)

        # diag_table updates
        self.diag_pert = self.indata.get("diag_pert", False)
        self.diag_path = self.full_path("diag_dir_name")

        # configuration updaters (MOM_override, hence needs to update mom6updater handler
        self.mom6updater = MOM6Updater(yamlfile)

        # metadata
        force_restart = self.indata.get("force_restart", False)
        self.startfrom = self.indata["startfrom"]
        startfrom_str = str(self.startfrom).strip().lower().zfill(3)
        self.metadata = MetaData(
            startfrom_str,
            force_restart,
            self.base_path,
            PERTURB_BRANCH_NAME,
        )

        # PBS job manager and experiment runs
        nruns = self.indata.get("nruns", 0)
        self.pbsjobmanager = PBSJobManager(
            self.dir_manager, self.check_duplicate_jobs, nruns
        )

    def manage_perturb_expt(self) -> None:
        """
        Sets up perturbation experiments based on the YAML configuration.

        This function processes various filenames defined in the YAML configuration,
        which may include,
        1. namelist files (`_in`, `.nml`),
        2. MOM6 input files (`MOM_input`),
        3. `nuopc.runconfig`,
        4. `nuopc.runseq` (currently only for the coupling timestep).

        Raises:
            UserWarning: If no parameter tuning configurations are provided.
        """
        # main section, top level key that groups different namelists
        namelists = self.indata.get("namelists")
        if not namelists:
            warnings.warn(
                "\nNO namelists were provided, hence skipping parameter-tunning tests!",
                UserWarning,
            )
            return

        for blockname, blockcontents in namelists.items():
            if not blockname.startswith(BLOCK_NAME):
                raise RuntimeError(f"Block name must start with {BLOCK_NAME}")

            if not blockcontents:
                continue

            self._process_namelist_block(blockname, blockcontents)

    def _process_namelist_block(
        self, blockname: str, blockcontents: dict[str, list | dict]
    ) -> None:
        """
        Process each parameter block in the namelist.

        Args:
            blockname (str): Name of a parameter block.
            blockcontents (dict[str, list|dict]): The content of each parameter block.
        """
        # user-defined perturb experiment directory names
        expt_dir_name = self._define_experiment_directories(blockname)
        # count groups under each parameter block
        self.group_count = self._count_nested_groups(blockcontents, expt_dir_name)
        self.tmp_count = 0

        for filename, params in blockcontents.items():
            if filename.startswith(expt_dir_name):
                self.expt_names = params
                self.num_expts = len(self.expt_names)
            elif isinstance(params, list):
                raise ValueError(
                    "The experiment names may not be set properly or "
                    "the YAML input contain invalid data."
                )
            else:
                self._process_params_cross_files(filename, params)

        # reset user-defined dirs
        self._reset_expt_names()

    def _process_params_cross_files(self, filename: str, filecontent: dict) -> None:
        """
        Processes all parameter groups cross files.

        Args:
            filename (str): The name of the file being processed.
            filecontent (dict): The content of the file, including groups and related name_dict,
                                where name_dict is the value dict under each group name,
                                in anther word, they are the actual parameters need to be tuned.
        """
        for groupname, name_dict in filecontent.items():
            self.tmp_count += 1

            if name_dict:
                self._generate_combined_dicts(groupname, name_dict, filename)
                self.setup_expts(filename)

    def _generate_combined_dicts(
        self, groupname: str, name_dict: dict, filename: str
    ) -> None:
        """
        Generates dictionaries with experiment-specific parameter values.

        Args:
            groupname (str): The name of the group.
            name_dict (dict): Dictionary containing parameter mappings.
            filename (str): Name of the file being processed.
        """
        if filename.startswith("MOM_input"):
            mom_input_parser = self.mom6updater.parser_mom6_input(
                os.path.join(self.base_path, "MOM_input")
            )
            commt_dict = mom_input_parser.commt_dict
        else:
            commt_dict = None

        list_of_param_dict_change = []
        list_of_groupname = []

        for i in range(self.num_expts):
            # specific for `submodels` keyword in `config.yaml` of access-om2
            # and `input` keyword in `config.yaml` of access-om3
            name_dict = self._preprocess_nested_dicts(name_dict)

            param_dict_change = {}
            for k, v in name_dict.items():
                if isinstance(v, list) and not isinstance(v[0], list):  # flat list
                    # Handle top-level lists like 'ncpus', 'mem', 'walltime', 'exe'...
                    param_dict_change[k] = v[i]
                elif isinstance(v, list) and all(isinstance(item, list) for item in v):
                    # nested lists
                    param_dict_change[k] = v[i]
                elif isinstance(v, dict):
                    # Handle the nested dicts, such as 'modules' in the config.yaml etc.
                    param_dict_change[k] = self._handle_nested_dict(v, i)

            list_of_groupname.append(groupname)
            list_of_param_dict_change.append(param_dict_change)
        self.list_of_param_dict_change = list_of_param_dict_change

        if filename == "MOM_input":
            self.commt_dict_change = {k: commt_dict.get(k, "") for k in name_dict}
        elif filename.endswith(("_in", ".nml", ".xml")) or filename in (
            ("nuopc.runconfig", "nuopc.runseq")
        ):
            self.list_of_groupname = list_of_groupname

    def _preprocess_nested_dicts(self, input_data: dict) -> dict:
        """
        Pre-processes nested dict with lists,
        ensuring proper formatting for experiment processing.

        Args:
            input_data (dict): Dictionary containing parameter mappings with nested structures.

        Returns:
            dict: A restructured dict where lists of dicts are grouped for each experiment.
        """
        res_dicts = {}
        for key, values in input_data.items():
            # Lists of dictionaries
            if isinstance(values, list) and all(isinstance(v, dict) for v in values):
                res_dicts[key] = self._group_submodels(values)
            elif isinstance(values, list) and isinstance(values[0], list):
                res_dicts[key] = list(map(list, zip(*values)))
            else:
                res_dicts[key] = values

        return res_dicts

    def _group_submodels(self, submodels: list[dict]) -> list[list[dict]]:
        """
        Groups submodel dictionaries by experiment index.

        Args:
            submodels (list[dict]): List of submodel dictionaries.

        Returns:
            list[list[dict]]: A nested list where each inner list corresponds to an experiment.
        """
        grouped_submodels = [[] for _ in range(self.num_expts)]

        for submodel in submodels:
            for i in range(self.num_expts):
                grouped_submodels[i].append(
                    self._extract_values_for_experiment(submodel, i)
                )

        return grouped_submodels

    def _extract_values_for_experiment(self, submodel: dict, index: int) -> dict:
        """
        Extracts experiment-specific values from a submodel dictionary.

        Args:
            submodel (dict): Dictionary containing parameter mappings.
            index (int): Index of the experiment.

        Returns:
            dict: Dictionary with extracted values for the specified experiment.
        """
        extracted_values = {}

        for param, value in submodel.items():
            if isinstance(value, list) and all(
                isinstance(item, list) for item in value
            ):
                # Nested lists
                extracted_values[param] = [sub_val[index] for sub_val in value]
            elif isinstance(value, list):
                extracted_values[param] = value[index]
            else:
                extracted_values[param] = value

        return extracted_values

    def _handle_nested_dict(self, nested_dict: dict, index: int) -> dict:
        """
        Recursively handles nested dictionaries, selecting experiment-specific values.

        Args:
            nested_dict (dict): The dictionary containing nested parameters.
            index (int): The index of the experiment.

        Returns:
            dict: A processed dictionary containing values relevant to the specific experiment.
        """
        processed_dict = {}
        for sub_k, sub_v in nested_dict.items():
            if isinstance(sub_v, list) and isinstance(sub_v[0], list):
                # nested list
                processed_dict[sub_k] = [sub_v_item[index] for sub_v_item in sub_v]
            elif isinstance(sub_v, list):
                # flat list
                processed_dict[sub_k] = sub_v[index]
            elif isinstance(sub_v, dict):
                # nested dict
                processed_dict[sub_k] = self._handle_nested_dict(sub_v, index)
            else:
                # flat dict
                processed_dict[sub_k] = sub_v
        return processed_dict

    def setup_expts(self, filename: str) -> None:
        """
        Configures and initialises perturbation experiments.

        Args:
            filename (str): The filename of the configuration being updated.
        """
        for i, param_dict in enumerate(self.list_of_param_dict_change):
            expt_name = self.expt_names[i]

            # perturbation experiment path
            expt_path = os.path.join(self.dir_manager, self.test_path, expt_name)

            self._clone_expt_directory(expt_path)

            if self.tmp_count == self.group_count:
                # update diag_table if enabled
                update_diag_table(
                    expt_path,
                    self.diag_path,
                    self.diag_pert,
                    self.model,
                )

                # update metadata
                self.metadata.update_medata(expt_path, param_dict)

                # update jobname same as perturbation experiment name
                self.configupdater.update_perturb_jobname(expt_path, expt_name)

            # Update configuration files based on the filename
            print(f"Updating parameters for {expt_name}: {param_dict}")
            self._update_configuration_files(filename, expt_path, param_dict, i)

            # run experiment jobs
            if self.tmp_count == self.group_count:
                self.pbsjobmanager.pbs_job_runs(expt_path)

    def _update_configuration_files(
        self, filename: str, expt_path: str, param_dict: dict, index: int
    ) -> None:
        """
        Updates experiment-specific configuration files based on the filename.

        Args:
            filename (str): The name of the configuration file being updated.
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The parameter dictionary containing updates.
            index (int): The index of the current experiment.
        """
        if filename == "MOM_input":
            self.mom6updater.override_mom6_params(
                expt_path, param_dict, self.commt_dict_change
            )
        elif filename.endswith("_in") or filename.endswith(".nml"):
            self.f90nmlupdater.update_nml_params(
                expt_path, param_dict, filename, self.list_of_groupname, index
            )
        elif filename == "nuopc.runseq":
            self.nuopcrunsequpdater.update_cpl_dt_params(
                expt_path, param_dict, filename
            )
        elif filename == "config.yaml":
            self.configupdater.update_config_params(expt_path, param_dict, filename)
        elif filename == "nuopc.runconfig":
            self.nuopcrunconfigupdater.update_runconfig_params(
                expt_path, param_dict, filename, self.list_of_groupname, index
            )
        elif filename.endswith(".xml"):
            self.xmlupdater.update_xml_elements(
                expt_path, param_dict, filename, self.list_of_groupname, index
            )

    def _define_experiment_directories(self, blockname: str) -> str:
        """
        Defines the experiment directory names.

        Args:
            blockname (str): The base name for the experiment block.

        Returns:
            str: The formatted directory name.
        """
        return f"{blockname}_dirs"

    def _count_nested_groups(self, blockcontents: dict, expt_dir_name: str) -> int:
        """
        Counts the number of nested groups within each filename.

        Args:
            block_contents (dict): The dictionary containing experiment parameters.
            expt_dir_name (str): The directory name for the experiments.

        Returns:
            int: The total number of nested groups.
        """
        group_count = 0
        for filenm, groups in blockcontents.items():
            if filenm == expt_dir_name:
                continue
            if isinstance(groups, dict):
                for inner_value in groups.values():
                    if isinstance(inner_value, dict):
                        group_count += 1
        return group_count

    def _reset_expt_names(self) -> None:
        """
        Resets user-defined perturbation experiment names.
        """
        self.expt_names = None

    def _clone_expt_directory(self, expt_path: str) -> None:
        """
        Clones the control experiment directory for perturbation experiments.

        Args:
            expt_path (str): The target path where the new experiment directory will be created.
        """
        if not os.path.exists(expt_path):
            # automatically leave a commit with expt uuid
            command = (
                f"payu clone -B {self.base_branch_name} "
                f"-b {PERTURB_BRANCH_NAME} {self.base_path} {expt_path}"
            )
        else:
            # syncs all changes from base to expt in case control experiment is modified
            command = (
                "rsync --quiet "
                "--exclude='archive/' "
                "--exclude='docs/' "
                "--exclude='manifests/' "
                "--exclude='.git/' "
                "--exclude='.github/' "
                "--exclude='testing/' "
                "--exclude='fd.yaml' "
                "--exclude='README.md' "
                f"{self.base_path}/ {expt_path}/"
            )

        subprocess.run(command, shell=True, check=True)
