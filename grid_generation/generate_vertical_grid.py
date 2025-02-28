# Copyright 2025 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# =========================================================================================
# Generate a vertical grid for MOM using a hyperbolic tangent function.
#
# This script creates a vertical grid and writes it to a NetCDF file.
# This script relates to the article "Stewart, K.D., Hogg, A.M., Griffies, S.M., Heerdegen, A.P., Ward, M.L., Spence, P. and England, M.H., 2017. Vertical resolution of baroclinic modes in global ocean models. Ocean Modelling, 113, pp.50-65."
#
# Usage:
# Run the script with command-line arguments to specify:
#   - H: Maximum ocean depth (meters)
#   - dzd: Maximum grid spacing at depth (meters)
#   - min_dz: Minimum grid spacing at the surface (meters)
#   - depfac: Tuning parameter for grid sharpness
#
# Example command to generate KDS75 grid or 025-degree OM3 vertical grid with 75 levels:
# python generate_vertical_grid.py --H 6000 --dzd 200 --min_dz 1 --depfac 1.101
#
# Contact:
#    Ezhilsabareesh Kannadasan <ezhilsabareesh.kannadasan@anu.edu.au>
#    This script was originally developed by Kial Stewart.
# Dependencies:
#   - netCDF4
#   - numpy
# =========================================================================================

import os
from datetime import datetime

import argparse
import netCDF4 as nc
import numpy as np

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Generate a vertical grid for ocean models."
)
parser.add_argument(
    "--H", type=float, required=True, help="Maximum ocean depth (meters)"
)
parser.add_argument(
    "--dzd", type=float, required=True, help="Maximum grid spacing at depth (meters)"
)
parser.add_argument(
    "--min_dz",
    type=float,
    required=True,
    help="Minimum grid spacing at the surface (meters)",
)
parser.add_argument(
    "--depfac", type=float, required=True, help="Tuning parameter for grid sharpness"
)
parser.add_argument(
    "--output", type=str, default="ocean_vgrid.nc", help="Output NetCDF filename"
)
args = parser.parse_args()

H = args.H
dzd = args.dzd
min_dz = args.min_dz
depfac = args.depfac
output_filename = args.output

# Define a small constant to initialize the iteration and prevent numerical issues
epsilon = 0.001


def f_all(kk):
    return np.tanh(np.pi * ((kk) / (H * depfac))) * dzd + epsilon


delta_z = [0, epsilon]
prop_z = [0, epsilon]

while prop_z[-1] + delta_z[-1] < 1.2 * H:
    aa = np.linspace(1.0, 1.5, 10000)
    bb = np.zeros(len(aa))
    loopkill = 1.0
    ii = 0
    while loopkill > 0:
        bb[ii] = f_all(prop_z[-1] + (delta_z[-1] * aa[ii])) - (delta_z[-1] * aa[ii])
        loopkill = bb[ii]
        ii += 1
    aa_bb = np.polyfit(aa[: ii - 1], bb[: ii - 1], 1)
    dznew = delta_z[-1] * (np.abs(aa_bb[1] / aa_bb[0]))
    delta_z.append(dznew)
    prop_z.append(prop_z[-1] + delta_z[-1])

new_surf = np.max(np.where(np.array(delta_z) < min_dz))
real_prop_z = np.array(prop_z[new_surf:]) - prop_z[new_surf]
real_delta_z = np.array(delta_z[new_surf:])
real_prop_z = real_prop_z[real_prop_z < H]
real_delta_z = real_delta_z[: len(real_prop_z)]

this_file = os.path.normpath(__file__)

# Add some info about how the file was generated
runcmd = (
    f"python3 {os.path.basename(this_file)} --H={H} --depfac={depfac} "
    f"--dzd={dzd} "
    f"--min_dz={min_dz} "
    f"--output={output_filename} "
)

eddyfile = nc.Dataset(output_filename, "w", format="NETCDF4")
eddyfile.createDimension("nzv", len(real_prop_z))
v_grid = eddyfile.createVariable("v_grid", "f8", ("nzv",))
v_grid.units = "meters"
v_grid.standard_name = "cell_thickness"
v_grid.long_name = "vertical grid depth at top and bottom of each cell"
eddyfile.variables["v_grid"][:] = real_prop_z
eddyfile.setncatts({"history": get_provenance_metadata(this_file, runcmd)})
eddyfile.close()

print(
    f"SUCCESS!! You now have a vertical grid of {len(real_prop_z) - 1} levels with grid spacing ranging from {real_delta_z[0]} to {real_delta_z[-1]} written to file {output_filename}"
)
