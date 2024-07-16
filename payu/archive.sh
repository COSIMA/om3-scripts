#!/usr/bin/bash -i

source $(dirname "$0")/archive_scripts/archive_cice_restarts.sh
source $(dirname "$0")/archive_scripts/concat_ice_daily.sh

# module use /g/data/xp65/public/modules ; module load conda/access-med-0.7
python3 $(dirname "$0")/archive_scripts/build_intake_ds.py