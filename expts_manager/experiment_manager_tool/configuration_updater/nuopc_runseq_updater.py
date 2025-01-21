import re
import os


class NuopcRunSeqUpdater:
    @staticmethod
    def update_cpl_dt_nuopc_seq(seq_path, update_cpl_dt):
        """
        Updates only coupling timestep through nuopc.runseq.
        """
        with open(seq_path, "r") as f:
            lines = f.readlines()
        pattern = re.compile(r"@(\S*)")
        update_lines = []
        for l in lines:
            matches = pattern.findall(l)
            if matches:
                update_line = re.sub(r"@(\S+)", f"@{update_cpl_dt}", l)
                update_lines.append(update_line)
            else:
                update_lines.append(l)
        with open(seq_path, "w") as f:
            f.writelines(update_lines)

    @staticmethod
    def update_cpl_dt_params(expt_path, param_dict, parameter_block):
        """
        Updates coupling timestep parameters.

        Args:
            expt_path (str): The path to the experiment directory.
            param_dict (dict): The dictionary of parameters to update.
        """
        nuopc_runseq_file = os.path.join(expt_path, parameter_block)
        NuopcRunSeqUpdater.update_cpl_dt_nuopc_seq(
            nuopc_runseq_file, param_dict[next(iter(param_dict.keys()))]
        )
