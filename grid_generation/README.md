# CICE Grid Generation

These two scripts usign the 'esmgrids' package developed for ACCESS-OM2, to make the CICE grid files from the MOM super grid file.

As executing `python3 make_cice_grid.py` can fail on the login node, a shell script to use with pbs is provided. The shell script also captures the hh5 module used and the input files used. Run `qsub pbs_make_cice_grids.sh` to make the cice grids and kmt file at all 3 model resolutions.