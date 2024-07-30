#!/usr/bin/bash -i

source $(dirname "$0")/archive_scripts/archive_cice_restarts.sh
source $(dirname "$0")/archive_scripts/concat_ice_daily.sh

# modules:
# use:
#     - /g/data/hh5/public/modules
# load:
#     - conda/analysis

python3 $(dirname "$0")/archive_scripts/build_intake_ds.py