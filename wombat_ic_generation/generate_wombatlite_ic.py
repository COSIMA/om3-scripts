# Copyright 2023 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# =========================================================================================
# Generate constant initial conditions for WOMBATlite using grid from a provided file
#
# To run:
#   python generate_wombatlite_ic.py --grid-filename=<path-to-grid-file>
#       --variable-name=<variable-name> --ic-filename=<path-to-output-file>
#
# For more information, run `python generate_wombatlite_ic.py -h`
#
# The run command and full github url of the current version of this script is added to the
# metadata of the generated IC file. This is to uniquely identify the script and inputs used
# to generate the IC file. To produce IC files for sharing, ensure you are using a version
# of this script which is committed and pushed to github. For IC files intended for released
# configurations, use the latest version checked in to the main branch of the github repository.
#
# Contact:
#   Dougie Squire <dougal.squire@anu.edu.au>
#
# Dependencies:
#   argparse, xarray
# =========================================================================================

import os
import subprocess
import xarray as xr

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum


def main():
    parser = argparse.ArgumentParser(
        description="Generate constant initial conditions for WOMBATlite using grid from provided file."
    )

    parser.add_argument(
        "--grid-filename",
        required=True,
        help="The path to a file containing a variable to copy the grid from.",
    )

    parser.add_argument(
        "--variable-name",
        required=True,
        help="The name of the variable to copy the grid from.",
    )

    parser.add_argument(
        "--ic-filename",
        required=True,
        help="The path to the initial condition file to be outputted.",
    )

    args = parser.parse_args()
    grid_filename = os.path.abspath(args.grid_filename)
    variable_name = args.variable_name
    ic_filename = args.ic_filename

    this_file = os.path.normpath(__file__)

    # Add some info about how the file was generated
    runcmd = (
        f"python3 {this_file} --grid-filename={os.path.abspath(grid_filename)} "
        f"--variable-name={variable_name} --ic-filename={os.path.abspath(ic_filename)}"
    )

    global_attrs = {
        "history": get_provenance_metadata(this_file, runcmd),
        "inputFile": f"{grid_filename} (md5 hash: {md5sum(grid_filename)})",
    }

    # Generate the initial conditions
    init_vars = {
        "phy": (0.01e-6, "mol kg-1"),
        "zoo": (0.01e-6, "mol kg-1"),
        "det": (0.01e-6, "mol kg-1"),
        "caco3": (0.01e-6, "mol kg-1"),
        "det_sediment": (0.0, "mol m-2"),
        "caco3_sediment": (0.0, "mol m-2"),
    }

    xr.set_options(keep_attrs=True)
    template = xr.open_dataset(
        grid_filename,
        decode_cf=False,
        decode_times=False,
    )[variable_name].compute()
    ds = {}
    for name, (const, units) in init_vars.items():
        da = 0 * template + const
        da.attrs["units"] = units
        da.attrs["long_name"] = name
        ds[name] = da
    ds = xr.Dataset(ds)
    ds.attrs = global_attrs

    ds.to_netcdf(ic_filename)


if __name__ == "__main__":
    import argparse

    main()
