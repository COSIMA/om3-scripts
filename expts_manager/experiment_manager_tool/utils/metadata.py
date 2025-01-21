import os
from experiment_manager_tool.utils.ryaml_handler import (
    read_yaml,
    write_yaml,
    LiteralString,
)


class MetaData:
    def __init__(
        self,
        startfrom_str: str,
        force_restart: bool,
        base_path: str,
        branch_perturb: str,
        base_branch_name: str,
    ) -> None:
        self.startfrom_str = startfrom_str
        self.force_restart = force_restart
        self.base_path = base_path
        self.base_dir_name = os.path.dirname(self.base_path)
        self.branch_perturb = branch_perturb
        self.base_branch_name = base_branch_name

    def update_medata(self, expt_path: str, param_dict: dict) -> None:
        # symlink restart directories
        restartpath = self._generate_restart_symlink(expt_path)
        self._update_metadata_yaml_perturb(expt_path, param_dict, restartpath)

    def _generate_restart_symlink(self, expt_path: str) -> str:
        """
        Generates a symlink to the restart directory if needed.

        Args:
            expt_path (str): The path to the experiment directory.
        """
        if self.startfrom_str != "rest":
            link_restart = os.path.join("archive", "restart" + self.startfrom_str)
            # restart dir from control experiment
            restartpath = os.path.realpath(os.path.join(self.base_path, link_restart))
            # restart dir symlink for each perturbation experiment
            dest = os.path.join(expt_path, link_restart)

            # only generate symlink if it doesnt exist or force_restart is enabled
            if (
                not os.path.islink(dest)
                or self.force_restart
                or (os.path.islink(dest) and not os.path.exists(os.readlink(dest)))
            ):
                if os.path.exists(dest) or os.path.islink(dest):
                    os.remove(dest)  # remove symlink
                    print(f"-- Remove restart symlink: {dest}")
                os.symlink(restartpath, dest)  # generate a new symlink
                if self.force_restart:
                    print(f"-- Restart symlink has been forced to be : {dest}")
                else:
                    print(f"-- Restart symlink: {dest}")
            # print restart symlink on the screen
            else:
                print(f"-- Restart symlink: {dest}")
        else:
            restartpath = "rest"
            print(f"-- Restart symlink: {restartpath}")

        return restartpath

    def _update_metadata_yaml_perturb(
        self, expt_path: str, param_dict: dict, restartpath: str
    ) -> None:
        """
        Updates the `metadata.yaml` file with relevant metadata.

        Args:
            expt_path (str): The path to the perturbation experiment directory.
            param_dict (dict): The dictionary of parameters to include in metadata.
        """
        metadata_path = os.path.join(expt_path, "metadata.yaml")
        metadata = read_yaml(metadata_path)  # load metadata of each perturbation
        self._update_metadata_description(metadata, restartpath)  # update `description`

        # remove None comments from `description`
        self._remove_metadata_comments("description", metadata)
        keywords = self._extract_metadata_keywords(param_dict)

        # extract parameters from the change list, and update `keywords`
        metadata["keywords"] = (
            f"{self.base_dir_name}, {self.branch_perturb}, {keywords}"
        )

        # remove None comments from `keywords`
        self._remove_metadata_comments("keywords", metadata)

        write_yaml(metadata, metadata_path)  # write to file

    def _remove_metadata_comments(self, key, metadata):
        """
        Removes comments after the key in metadata.
        """
        if key in metadata:
            metadata.ca.items[key] = [None, None, None, None]

    def _update_metadata_description(self, metadata, restartpath):
        """
        Updates metadata description with experiment details.
        """
        tmp_string1 = (
            f"\nNOTE: this is a perturbation experiment, but the description above is for the control run."
            f"\nThis perturbation experiment is based on the control run {self.base_path} from {self.base_branch_name}"
        )
        tmp_string2 = f"\nbut with initial condition {restartpath}."
        desc = metadata["description"]
        if desc is None:
            desc = ""
        if tmp_string1.strip() not in desc.strip():
            desc += tmp_string1
        if tmp_string2.strip() not in desc.strip():
            desc += tmp_string2
        metadata["description"] = LiteralString(desc)

    def _extract_metadata_keywords(self, param_change_dict):
        """
        Extracts keywords from parameter change dictionary.
        """
        keywords = ", ".join(param_change_dict.keys())
        return keywords
