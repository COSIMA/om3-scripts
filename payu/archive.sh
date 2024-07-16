#!/usr/bin/bash -i

source /g/data/tm70/as2285/om3-scripts/payu/archive_scripts/archive_cice_restarts.sh
source /g/data/tm70/as2285/om3-scripts/payu/archive_scripts/concat_ice_daily.sh

# module use /g/data/xp65/public/modules ; module load conda/access-med-0.7
python3 /g/data/tm70/as2285/om3-scripts/payu/archive_scripts/build_intake_ds.py