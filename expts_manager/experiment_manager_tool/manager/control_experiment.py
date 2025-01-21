import os
from experiment_manager_tool.git_manager.git_manager import payu_clone_from_commit_hash
from experiment_manager_tool.utils.util_functions import update_diag_table
from experiment_manager_tool.configuration_updater.f90nml_updater import f90nmlUpdater
from experiment_manager_tool.configuration_updater.nuopc_runconfig_updater import NuopcRunConfigUpdater
from experiment_manager_tool.configuration_updater.nuopc_runseq_updater import NuopcRunSeqUpdater
from experiment_manager_tool.configuration_updater.config_updater import ConfigUpdater
from experiment_manager_tool.configuration_updater.mom6_updater import MOM6Updater
from experiment_manager_tool.configuration_updater.xml_updater import XMLUpdater
from experiment_manager_tool.mixins.mixins import FullPathMixin
from experiment_manager_tool.pbs_job_manager.pbs_job_manager import PBSJobManager
from experiment_manager_tool.utils.base_manager import BaseManager

import xml

class ControlExperiment(BaseManager, FullPathMixin):
    def __init__(self, yamlfile: str) -> None:
        super().__init__(yamlfile)
        
        # YAML inputs for control experiment
        self.base_url = self.indata.get("base_url")
        self.base_commit = self.indata.get("base_commit")
        self.base_branch_name = self.indata.get("base_branch_name")
        self.base_path = self.full_path("base_dir_name")

        # diag_table updates
        self.diag_ctrl = self.indata.get("diag_ctrl", False)
        self.diag_path = self.full_path("diag_dir_name")
        
        # configuration updaters
        self.f90nmlupdater = f90nmlUpdater()
        self.configupdater = ConfigUpdater()
        self.nuopcrunsequpdater = NuopcRunSeqUpdater()
        self.xmlupdater = XMLUpdater()
        self.nuopcrunconfigupdater = NuopcRunConfigUpdater(yamlfile)
        self.mom6updater = MOM6Updater(yamlfile)

        # PBS job manager and control runs
        self.check_duplicate_jobs = self.indata.get("check_duplicate_jobs", True)
        ctrl_nruns = self.indata.get("ctrl_nruns", 0)
        self.pbsjobmanager = PBSJobManager(self.dir_manager, self.check_duplicate_jobs, ctrl_nruns)

    def manage_experiment(self) -> None:
        print(f"-- Setting up control experiment at {self.base_path}")

        if os.path.exists(self.base_path):
            print(f"-- Control experiment {self.base_path} already exists, hence skipping cloning.")
            print(f"   However, control experiment can still be updated based on the YAML inputs.")
        else:
            payu_clone_from_commit_hash(
                self.base_url,
                self.base_commit,
                self.base_branch_name,
                self.base_path,
            )

        # update diag_table if enabled
        update_diag_table(self.base_path,
                          self.diag_path,
                          self.diag_ctrl,
                          self.model,
                          )

        # setup control experiment
        self._setup_control_expt()

        # run control experiment
        self.pbsjobmanager.pbs_job_runs(self.base_path)

    def _setup_control_expt(self) -> None:
        """
        Modifies parameters based on the input YAML configuration for the control experiment.

        Updates configuration files:
            1. config.yaml, 
            2. f90 namelist files (.in, .nml),
            3. nuopc.runconfig,
            4. MOM_input,
            5. nuopc.runseq,
            for the control experiment if needed.
        """
        for curr_dir, sub_dirs, files_curr_dir in os.walk(self.base_path):
            sub_dirs[:] = [tmp_d for tmp_d in sub_dirs if ".git" not in tmp_d]
            for f in files_curr_dir:
                if ".git" in f:
                    continue

                target_file = os.path.relpath(os.path.join(curr_dir, f), self.base_path)
                yaml_data = self.indata.get(target_file)

                if yaml_data:
                    # Updates config entries from f90nml files
                    if target_file.endswith("_in") or target_file.endswith(".nml"):
                        self.f90nmlupdater.update_nml_params(self.base_path, yaml_data, target_file)

                    # Updates config entries from `nuopc.runconfig`
                    if target_file == "nuopc.runconfig":
                        self.nuopcrunconfigupdater.update_runconfig_params(self.base_path, yaml_data, target_file)

                    # Updates config entries from `config_yaml`
                    if target_file == "config.yaml":
                        self.configupdater.update_config_params(self.base_path, yaml_data, target_file)

                    # Updates config entries from `MOM_input`
                    if target_file == "MOM_input":
                        self.mom6updater.update_mom6_params(self.base_path, yaml_data, target_file)

                    # Update only coupling timestep from `nuopc.runseq`
                    if target_file == "nuopc.runseq":
                        self.nuopcrunsequpdater.update_cpl_dt_params(self.base_path, yaml_data, target_file)

                    # Update only xml entries from .xml
                    if target_file.endswith(".xml"):
                        self.xmlupdater.update_xml_elements(self.base_path, yaml_data, target_file)