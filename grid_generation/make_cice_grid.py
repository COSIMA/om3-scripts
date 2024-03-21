"""
Script: make_cice_grid.py
Description: 
This script generates a CICE grid from the MOM super grid provided in the input NetCDF file.

Usage:
python make_cice_grid.py <ocean_hgrid> <ocean_hgrid>
- ocean_hgrid: Path to the MOM super grid NetCDF file.
- ocean_mask: Path to the corresponding mask NetCDF file.

"""


#!/usr/bin/env python3
# File based on https://github.com/COSIMA/access-om2/blob/29118914d5224152ce286e0590394b231fea632e/tools/make_cice_grid.py

import sys
import os
import argparse

my_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(my_dir, 'esmgrids'))

from esmgrids.mom_grid import MomGrid  # noqa
from esmgrids.cice_grid import CiceGrid  # noqa


def md5sum(filename):
    from hashlib import md5
    from mmap import mmap, ACCESS_READ
    
    with open(filename) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
        return md5(file).hexdigest()

"""
Create CICE grid.nc and kmt.nc from MOM ocean_hgrid.nc and ocean_mask.nc
"""

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('ocean_hgrid', help='ocean_hgrid.nc file')
    parser.add_argument('ocean_mask', help='ocean_mask.nc file')

    args = parser.parse_args()

    mom = MomGrid.fromfile(args.ocean_hgrid, mask_file=args.ocean_mask)

    cice = CiceGrid.fromgrid(mom)


    grid_file = os.path.join('grid.nc')
    mask_file = os.path.join('kmt.nc')

    cice.create_gridnc(grid_file)

    # Add versioning information    
    cice.grid_f.inputfile = f"{args.ocean_hgrid}"
    cice.grid_f.inputfile_md5 = md5sum(args.ocean_hgrid)
    cice.grid_f.history_command = f"python make_CICE_grid.py {args.ocean_hgrid} {args.ocean_mask}"

    cice.write()

    cice.create_masknc(mask_file)

    # Add versioning information    
    cice.mask_f.inputfile = f"{args.ocean_mask}"
    cice.mask_f.inputfile_md5 = md5sum(args.ocean_mask)
    cice.mask_f.history_command = f"python make_CICE_grid.py {args.ocean_hgrid} {args.ocean_mask}"

    cice.write_mask()

if __name__ == '__main__':
    sys.exit(main())
