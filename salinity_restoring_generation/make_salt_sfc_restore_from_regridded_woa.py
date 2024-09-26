#!/usr/bin/env python3
# Copyright 2023 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Contact: Ezhilsabareesh Kannadasan <ezhilsabareesh.kannadasan@anu.edu.au>

"""
This script processes and smooths sea water salinity data from the initial conditions NetCDF files generated using https://github.com/COSIMA/initial_conditions_access-om2.
It applies a uniform smoothing filter to the surface layer (0m depth) of the salinity for each month and concatenates the smoothed data into a single output NetCDF file.

The input files are 'woa23_ts_<month>_mom025.nc',

The script creates an output file 'salt_sfc_restore.nc' which contains the smoothed 
and concatenated salinity data for 12 months.

Usage:
    python make_salt_sfc_restore_from_regridded_woa.py <input_directory> <output_directory>

Example:
    python make_salt_sfc_restore_from_regridded_woa.py /path/to/input/dir /path/to/output/dir

Command-line arguments:
    - input_directory: The directory containing the initial conditions NetCDF files.
    - output_directory: The directory where the output smoothed and concatenated NetCDF file will be saved.
"""

import xarray as xr
import numpy as np
from scipy.ndimage import uniform_filter
import argparse
from pathlib import Path
import sys

# Add the root path for the common scripts
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum


def smooth2d(src):
    tmp_src = np.ndarray((src.shape[0] + 6, src.shape[1]))

    # Window size
    ws = 3

    tmp_src[ws:-ws, :] = src[:, :]
    tmp_src[:ws, :] = src[-ws:, :]
    tmp_src[-ws:, :] = src[:3, :]

    dest = uniform_filter(tmp_src, size=ws, mode="nearest")
    return dest[ws:-ws, :]


def main(input_path, output_path):
    variable_to_smooth = "salt"

    file_template = f"{input_path}/woa23_ts_{{:02d}}_mom025.nc"

    file_paths = [file_template.format(month) for month in range(1, 13)]

    ds = xr.open_mfdataset(file_paths, chunks={"GRID_Y_T": -1, "GRID_X_T": -1})

    # Get the sea surface salinity
    salt_da = ds[variable_to_smooth].isel(ZT=0)

    # Smooth the salinity in x & y (for each month)
    salt_smoothed_da = xr.apply_ufunc(
        smooth2d,
        salt_da,
        input_core_dims=[["GRID_Y_T", "GRID_X_T"]],
        output_core_dims=[["GRID_Y_T", "GRID_X_T"]],
        vectorize=True,
        dask="parallelized",
    )

    salt_smoothed_da = salt_smoothed_da.assign_attrs(
        {
            "standard_name": "sea_water_salinity",
            "long_name": "Smoothed sea water salinity at level 0m",
            "units": "1",
        }
    )

    salt_smoothed_da["time"] = salt_smoothed_da.time.assign_attrs({"modulo": " "})

    # Save
    output_file = f"{output_path}/salt_sfc_restore.nc"
    salt_smoothed_da.to_netcdf(output_file)

    print(f"Concatenated and smoothed data saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process and concatenate NetCDF files with smoothing."
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to the directory containing input NetCDF files.",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to the directory where the output NetCDF file will be saved.",
    )
    args = parser.parse_args()

    main(args.input_path, args.output_path)
