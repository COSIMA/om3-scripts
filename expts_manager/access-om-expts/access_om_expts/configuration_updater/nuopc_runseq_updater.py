"""
nuopc.runseq Updater for the experiment management.

This module provides utilities for updating `nuopc.runseq` files, specifically
modifying the coupling timestep.
"""

import re
import os


class NuopcRunSeqUpdater:
    """
    A utility class for updating the coupling timestep in `nuopc.runseq`.

    Methods:
        - `update_cpl_dt_nuopc_seq`: Updates the coupling timestep in the run sequence.
        - `update_cpl_dt_params`: Updates coupling parameters using an experiment directory.
    """

    @staticmethod
    def update_cpl_dt_nuopc_seq(seq_path, update_cpl_dt):
        """
        Updates only the coupling timestep in the `nuopc.runseq` file.

        Args:
            seq_path (str): Path to the `nuopc.runseq` file.
            update_cpl_dt (str): New coupling timestep value to update in the file.
        """
        with open(seq_path, "r", encoding="utf-8") as f:
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
        with open(seq_path, "w", encoding="utf-8") as f:
            f.writelines(update_lines)

    @staticmethod
    def update_cpl_dt_params(expt_path, param_dict, filename):
        """
        Updates the coupling timestep parameters in `nuopc.runseq`.

        Args:
            expt_path (str): Path to the experiment directory.
            param_dict (dict): Dictionary of parameters to update.
            filename (str): Name of the `nuopc.runseq` file.
        """
        nuopc_runseq_file = os.path.join(expt_path, filename)
        NuopcRunSeqUpdater.update_cpl_dt_nuopc_seq(
            nuopc_runseq_file, param_dict[next(iter(param_dict.keys()))]
        )
