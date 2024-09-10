#!/usr/bin/bash -i

source $(dirname "$0")/archive_scripts/archive_cice_restarts.sh
source $(dirname "$0")/archive_scripts/concat_ice_daily.sh
source $(dirname "$0")/archive_scripts/standardise_mom6_filenames.sh
python3 $(dirname "$0")/archive_scripts/build_intake_ds.py
