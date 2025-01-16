import os
import warnings
import subprocess
from experiment_manager_tool.utils.util_functions import update_diag_table
from experiment_manager_tool.utils.metadata import MetaData
from experiment_manager_tool.configuration_updater.mom6_updater import MOM6Updater
from experiment_manager_tool.manager.control_experiment import ControlExperiment
from experiment_manager_tool.pbs_job_manager.pbs_job_manager import PBSJobManager


class PerturbExperiment(ControlExperiment):
    """
    """
    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)

        # class setup
        self.expt_names = None
        self.num_expts = None
        self.tmp_count = 0
        self.group_count = None

        # Parameter-related initialisation
        self.commt_dict_change = {}  # MOM6 comment
        self.list_of_param_dict_change = [] # ALL parameter changes
        self.list_of_groupname = [] # f90nml parameter

        # diag_table updates
        self.diag_pert = self.indata.get("diag_pert", False)
        self.diag_path = self.full_path("diag_dir_name")

        # configuration updaters
        self.mom6updater = MOM6Updater(yamlfile)

        # metadata
        force_restart = self.indata.get("force_restart", False)
        self.startfrom = self.indata["startfrom"]
        startfrom_str = str(self.startfrom).strip().lower().zfill(3)
        self.metadata = MetaData(startfrom_str, force_restart, self.base_path, self.branch_perturb, self.base_branch_name)

        # PBS job manager and experiment runs
        nruns = self.indata.get("nruns", 0)
        self.pbsjobmanager = PBSJobManager(self.dir_manager, self.check_duplicate_jobs, nruns)

    def manage_perturb_expt(self) -> None:
        """
        Sets up perturbation experiments based on the configuration provided in `Expts_manager.yaml`.

        This function processes various parameter blocks defined in the YAML configuration, which may include
        1. namelist files (`_in`, `.nml`),
        2. MOM6 input files (`MOM_input`),
        3. `nuopc.runconfig`,
        4. `nuopc.runseq` (currently only for the coupling timestep).

        Raises:
            - Warning: If no namelist configurations are provided, the function issues a warning indicating that no parameter tuning tests will be conducted.
        """
        # main section, top level key that groups different namlists
        namelists = self.indata.get("namelists")
        if not namelists:
            warnings.warn(
                "\nNO namelists were provided, hence there are no parameter-tunning tests!",
                UserWarning,
            )
            return

        for blockname, blockcontents in namelists.items():
            if not blockcontents:
                continue

            self._process_namelist_block(blockname, blockcontents)
            
    def _process_namelist_block(self, blockname: str, blockcontents: dict[str, list|dict]) -> None:
        """
        Process each parameter block in the namelist.
        
        Args:
            blockname (str): Name of a parameter block, must starting with cross_block.
            blockcontents (dict[str, list|dict]): The content of each parameter block. 
        """
        expt_dir_name = self._user_defined_dirs(blockname)
        self.group_count = self._count_nested_groups(blockcontents, expt_dir_name)
        self.tmp_count = 0

        for filename, params in blockcontents.items():
            if filename.startswith(expt_dir_name):
                self.expt_names = params
                self.num_expts = len(self.expt_names)
            elif isinstance(params, list):
                raise ValueError("The experiment names may not be set properly or the YAML input contain invalid data.")
            else:
                self._process_params_cross_files(filename, params)

        # reset user-defined dirs
        self._reset_expt_names()

    def _process_params_cross_files(self, filename: str, filecontent: dict) -> None:
        """
        Processes all parameter groups cross files.
        
        Args:
            filename (str): The name of the file being processed.
            filecontent (dict): The content of the file, which includes groups and related name_dict,
                                where name_dict is the value dict under each group name, in anther word, they are the actual parameters need to be tuned. 
        """
        for groupname, name_dict in filecontent.items():
            self.tmp_count += 1

            if name_dict:
                self._generate_combined_dicts(groupname, name_dict, filename)
                self.setup_expts(filename)

    def _generate_combined_dicts(self, groupname: str, name_dict: dict, filename: str) -> None:
        """
        Generates a list of dictionaries where each dictionary contains all keys with values from the same index for multiple experiments.
        """
        if filename.startswith("MOM_input"):
            MOM_inputParser = self.mom6updater._parser_mom6_input(os.path.join(self.base_path, "MOM_input"))
            commt_dict = MOM_inputParser.commt_dict
        else:
            commt_dict = None

        list_of_param_dict_change = []
        list_of_groupname = []

        for i in range(self.num_expts):
            name_dict = self._preprocess_nested_dicts(name_dict)

            if any(len(v) != self.num_expts for v in name_dict.values() if isinstance(v, list)):
                raise ValueError(f"The length of values in {list(name_dict.keys())} is inconsistent with the number of experiments.")

            param_dict_change = {}
            for k, v in name_dict.items():
                if isinstance(v, list) and not isinstance(v[0], list): # flat list
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
        elif filename.endswith(("_in", ".nml")) or filename in (("config.yaml", "nuopc.runconfig", "nuopc.runseq")):
            self.list_of_groupname = list_of_groupname

    def _preprocess_nested_dicts(self, input_data: dict) -> dict:
        """
        Pre-processes nested dictionary with lists.
        """
        res_dicts = {}

        for tmp_key, tmp_values in input_data.items():
            if isinstance(tmp_values, list) and all(isinstance(v, dict) for v in tmp_values):
                grouped_submodels = [[] for _ in range(self.num_expts)]
                for submodel in tmp_values:
                    for i in range(self.num_expts):
                        tmp = {}
                        for k, v in submodel.items():
                            if isinstance(v, list) and all(isinstance(item, list) for item in v):
                                tmp[k] = [item[i] for item in v]
                            elif isinstance(v, list):
                                tmp[k] = v[i]
                            else:
                                tmp[k] = v
                        grouped_submodels[i].append(tmp)
                res_dicts[tmp_key] = grouped_submodels
            else:
                res_dicts[tmp_key] = tmp_values
        return res_dicts

    def _handle_nested_dict(self, nested_dict: dict, index: int) -> dict:
        """
        Recursively handles nested dictionaries (e.g., dictionaries with lists inside them).
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
        Sets up perturbation experiments.
        """
        for i, param_dict in enumerate(self.list_of_param_dict_change):
            expt_name = self.expt_names[i]

            # perturbation experiment path
            expt_path = os.path.join(self.dir_manager, self.test_path, expt_name)

            # generate perturbation experiment directory
            if os.path.exists(expt_path):
                if self.tmp_count == self.group_count:
                    print(f"-- not creating {expt_path} - already exists!")
            else:
                if self.tmp_count == 1:
                    print(f"Directory {expt_path} not exists, hence cloning template!")
                    self._clone_expt_directory(expt_path)

            if self.tmp_count == self.group_count:
                # update diag_table if enabled
                update_diag_table(expt_path,
                                self.diag_path,
                                self.diag_pert,
                                self.model,
                                )

                # update metadata
                self.metadata.update_medata(expt_path, param_dict)

                # update jobname same as perturbation experiment name
                self.configupdater.update_perturb_jobname(expt_path, expt_name)

            # update params for each parameter block
            print(f"-- tunning parameters: {param_dict}")
            if filename == "MOM_input":
                self.mom6updater.override_mom6_params(expt_path, param_dict, self.commt_dict_change)
            elif filename.endswith("_in") or filename.endswith(".nml"):
                self.f90nmlupdater.update_nml_params(expt_path, param_dict, filename, self.list_of_groupname, i)
            elif filename == "nuopc.runseq":
                self.nuopcrunsequpdater.update_cpl_dt_params(expt_path, param_dict, filename)
            elif filename == "config.yaml":
                self.configupdater.update_config_params(expt_path, param_dict, filename)
            elif filename == "nuopc.runconfig":
                self.nuopcrunconfigupdater.update_runconfig_params(expt_path, param_dict, filename, self.list_of_groupname, i)

            if self.tmp_count == self.group_count:
                self.pbsjobmanager.pbs_job_runs(expt_path)

    def _user_defined_dirs(self, blockname: str) -> str:
        """
        Defines experiment directory names
        """
        expt_dir_name = blockname + "_dirs"
        return expt_dir_name

    def _count_nested_groups(self, blockcontents: dict, expt_dir_name: str) -> int:
        """
        Counts the number of nested groups under each filename
        """
        group_count = 0
        for key, groups in blockcontents.items():
            # skip the user-defined expt directory name
            if key == expt_dir_name:
                continue
            if isinstance(groups, dict):
                for _, inner_value in groups.items():
                    if isinstance(inner_value, dict):
                        group_count += 1
        return group_count

    def _reset_expt_names(self):
        """
        Resets user-defined perturbation experiment names.
        """
        self.expt_names = None
        
    def _clone_expt_directory(self, expt_path: str) -> None:
        """
        Generates a new experiment directory by cloning the control experiment.
        Checks if the tuning parameter matches the control experiment,
        this validation currently applies only to `nml` files.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
        """
        # automatically leave a commit with expt uuid
        command = f"payu clone -B {self.base_branch_name} -b {self.branch_perturb} {self.base_path} {expt_path}"
        subprocess.run(command, shell=True, check=True)