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
import netCDF4 as nc
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
    # Variable to be processed
    variable_to_smooth = "salt"
    variable_to_exclude = "temp"

    # Template for file paths
    file_template = f"{input_path}/woa23_ts_{{:02d}}_mom025.nc"

    # Initialize lists to store data
    monthly_data = []
    time_values = []

    # Loop over each month and open the corresponding file
    for month in range(1, 13):
        # Construct the file name
        file_path = file_template.format(month)

        try:
            # Open the dataset
            ds = xr.open_dataset(file_path)

            # Process the variable to be smoothed
            if variable_to_smooth in ds.data_vars:
                data = ds[variable_to_smooth].isel(ZT=0).load()
                data_np = np.squeeze(data.values)
                # Append data to list
                monthly_data.append(data_np)
                time_values.append(
                    ds["time"].values[0]
                )  # Extract the actual time value
        except FileNotFoundError:
            print(f"File not found: {file_path}")

    # Concatenate the data across all months along the time dimension
    concatenated_data = np.stack(monthly_data, axis=0)

    # Loop through each month for smoothing
    smoothed_monthly_data = []
    for i in range(concatenated_data.shape[0]):
        # Smooth each month's data
        data_np_smoothed = smooth2d(concatenated_data[i, :, :])
        smoothed_monthly_data.append(data_np_smoothed)

    smoothed_data_np = np.stack(smoothed_monthly_data, axis=0)

    # Create a new NetCDF file using netCDF4
    output_file = f"{output_path}/salt_sfc_restore.nc"
    with nc.Dataset(output_file, "w", format="NETCDF4") as ncfile:
        # Create dimensions
        time_dim = ncfile.createDimension("time", None)  # Unlimited dimension
        lat_dim = ncfile.createDimension("lat", ds["GRID_Y_T"].shape[0])
        lon_dim = ncfile.createDimension("lon", ds["GRID_X_T"].shape[0])

        # Create coordinate variables
        times = ncfile.createVariable("time", "f4", ("time",))
        lats = ncfile.createVariable("lat", "f4", ("lat",))
        lons = ncfile.createVariable("lon", "f4", ("lon",))

        # Assign attributes to the coordinate variables
        lats.units = "degree_north"
        lats.long_name = "Nominal Latitude of cell center"
        lats.point_spacing = "uneven"
        lats.axis = "Y"

        lons.units = "degree_east"
        lons.long_name = "Nominal Longitude of cell center"
        lons.modulo = 360.0
        lons.point_spacing = "even"
        lons.axis = "X"

        times[:] = np.arange(0.5, 12.5, 1)  # Time values from 0.5 to 11.5
        times.units = "months since 0001-01-01 00:00:00"
        times.long_name = "time"
        times.cartesian_axis = "T"
        times.axis = "T"
        times.calendar_type = "noleap"
        times.standard_name = "time"
        times.climatology = "climatology_bounds"
        times.setncattr("modulo", " ")

        # Create the smoothed variable
        salt_var = ncfile.createVariable(
            "salt", "f4", ("time", "lat", "lon"), fill_value=-9.99e33
        )
        salt_var.standard_name = "sea_water_salinity"
        salt_var.long_name = "Smoothed sea water salinity at level 0m"
        salt_var.units = "1"

        # Assign the data to the coordinate variables
        lats[:] = ds["GRID_Y_T"].values
        lons[:] = ds["GRID_X_T"].values

        # Assign the smoothed data to the salt variable
        salt_var[:, :, :] = smoothed_data_np

        # Add global attributes
        this_file = Path(__file__).name
        runcmd = " ".join(sys.argv)  # Command used to run the code
        ncfile.history = get_provenance_metadata(this_file, runcmd)
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
