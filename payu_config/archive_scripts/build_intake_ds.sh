#!/usr/bin/bash
#PBS -l ncpus=24 
#PBS -l mem=96GB 
#PBS -q normal 
#PBS -l walltime=02:00:00
#PBS -l wd

module use /g/data/xp65/public/modules 
module load conda/analysis3-25.02

python3 $SCRIPTS_DIR/archive_scripts/build_intake_ds.py
