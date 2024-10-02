#!/usr/bin/bash
#PBS -l ncpus=24 
#PBS -l mem=96GB 
#PBS -q normal 
#PBS -l walltime=02:00:00
#PBS -l wd

module use /g/data/hh5/public/modules 
module load conda/analysis3-24.01

python3 $SCRIPTS_DIR/archive_scripts/build_intake_ds.py
