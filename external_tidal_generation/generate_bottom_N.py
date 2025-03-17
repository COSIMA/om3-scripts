# Copyright 2025 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# =========================================================================================
# Generate an N field (buoyancy frequency) from WOA climatology.
#
# This script creates a 3D stratification field from WOA temperature and salinity
# data, computes the buoyancy frequency (N) on a mid-depth grid, and then averages N
# over the bottom DEPTH_THRESHOLD meters of the water column for each (lat, lon) column.
#
# - If --depth-threshold > 0, compute a bottom-X meters average.
# - If --depth-threshold == 0 (default), compute a full water-column (depth-averaged) mean.
#
# Usage:
#    python3 generate_bottom_N.py \
#         --temp-file /path/to/woa_decav_t00_04.nc \
#         --sal-file /path/to/woa_decav_s00_04.nc \
#         [--depth-threshold 500.0] \
#         --output Nbot_freq.nc
#
# Contact:
#    Minghang Li <Minghang.Li1@anu.edu.au>
#    This script was originally developed by Luwei Yang <Luwei.Yang@anu.edu.au>
#
# Dependencies:
#   - gsw
#   - xarray
#   - xesmf
#   - numpy
# =========================================================================================

from pathlib import Path
import sys
import argparse
import os
import warnings
warnings.filterwarnings("ignore")

import xarray as xr
import numpy as np
import gsw
import xesmf as xe

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum


def load_woa_data(temp_file: str, sal_file: str) -> (xr.DataArray, xr.DataArray):
    """Load the WOA climatological temperature and salinity datasets."""
    temp_ds = xr.open_dataset(temp_file, decode_times=False)
    sal_ds = xr.open_dataset(sal_file, decode_times=False)

    sea_water_temp = temp_ds.t_an.squeeze().drop_vars("time", errors="ignore")
    sea_water_sal = sal_ds.s_an.squeeze().drop_vars("time", errors="ignore")
    return sea_water_temp, sea_water_sal


def compute_pressure(depth: xr.DataArray, lat: xr.DataArray, lon: xr.DataArray) -> xr.DataArray:
    """
    Compute a 3D pressure field (in dbar) from 1D depth and lat arrays.
    gsw.p_from_z expects negative depth.
    """
    depth_3d = depth.expand_dims({"lat": lat, "lon": lon})
    lat_3d = lat.expand_dims({"depth": depth, "lon": lon})
    pressure_3d = xr.apply_ufunc(
        lambda dep, la: gsw.p_from_z(-dep, la),
        depth_3d,
        lat_3d,
        input_core_dims=[["depth", "lat", "lon"]] * 2,
        output_core_dims=[["depth", "lat", "lon"]],
        vectorize=True,
    )
    return pressure_3d


def compute_stratification(
    sea_water_temp: xr.DataArray,
    sea_water_sal: xr.DataArray,
    pressure_3d: xr.DataArray,
    lat: xr.DataArray,
) -> (xr.DataArray, xr.DataArray):
    """
    Compute squared buoyancy frequency and mid pressures, then derive N and mid-depth.
    """
    N2_3D, p_mid = xr.apply_ufunc(
        gsw.Nsquared,
        sea_water_sal,
        sea_water_temp,
        pressure_3d,
        input_core_dims=[["depth", "lat", "lon"]] * 3,
        output_core_dims=[["depth_mid", "lat", "lon"]] * 2,
        vectorize=True,
    )
    # Compute N from N square
    N_3D = np.sqrt(N2_3D)

    # Compute mid-depth
    lat_broad, _ = xr.broadcast(lat, p_mid)
    depth_mid = -gsw.z_from_p(p_mid, lat_broad)  # Now depth_mid > 0
    return N_3D, depth_mid


def compute_bottom_average(
    N_3D: xr.DataArray,
    depth_mid: xr.DataArray,
    sea_water_temp: xr.DataArray,
    depth: xr.DataArray,
    depth_threshold: float = 0.0,
) -> xr.DataArray:
    """
    Compute either a bottom-X meters average if depth_threshold>0,
    or a full-column (depth-averaged) mean if depth_threshold==0.
    """
    if depth_threshold > 0:
        # Broadcast depth
        depth_array = sea_water_temp * 0 + depth
        max_depth = depth_array.max(dim="depth", skipna=True)
        bottom_threshold = max_depth - depth_threshold

        # Create a mask
        mask_bottom = xr.where(
            (depth_mid >= bottom_threshold) & (depth_mid < max_depth),
            1,
            np.nan,
        )
        N_3D_bottom = N_3D * mask_bottom

        # average depth_mid
        N_3D_ave = N_3D_bottom.mean(dim="depth_mid", skipna=True) / (2 * np.pi)
    else:
        # full depth average
        N_3D_ave = N_3D.mean(dim="depth_mid", skipna=True) / (2 * np.pi)

    return N_3D_ave


def regrid_data(
    N_3D_ave: xr.DataArray, lon: xr.DataArray, lat: xr.DataArray
) -> xr.Dataset:
    """
    Regrid the averaged stratification data to a target grid (using the original lon/lat).
    """
    mask_array = ~np.isnan(N_3D_ave.values)
    ds = xr.Dataset(
        data_vars={
            "N_3D_ave": (("lat", "lon"), N_3D_ave.values),
            "mask": (("lat", "lon"), mask_array),
        },
        coords={"lon": lon, "lat": lat},
    )

    ds_out = xr.Dataset(
        {
            "lat": (["lat"], lat.values),
            "lon": (["lon"], lon.values),
        }
    )

    # Regrid
    regridder = xe.Regridder(ds, ds_out, "bilinear", extrap_method="inverse_dist")
    ds_out = regridder(ds)

    Nbot_data = xr.Dataset(
        {"Nbot": (("lat", "lon"), ds_out["N_3D_ave"].values)},
        coords={"lon": lon, "lat": lat},
    )
    return Nbot_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate bottom-Xm averaged stratification from WOA climatology."
    )
    parser.add_argument(
        "--depth-threshold",
        type=float,
        default=0.0,
        help="Bottom threshold in meters over which to average (default: 500).",
    )
    parser.add_argument(
        "--temp-file",
        type=str,
        required=True,
        help="Path to the WOA temperature NetCDF file.",
    )
    parser.add_argument(
        "--sal-file",
        type=str,
        required=True,
        help="Path to the WOA salinity NetCDF file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="Nbot_freq.nc",
        help="Output NetCDF filename (default: Nbot_freq.nc).",
    )
    args = parser.parse_args()

    # Load Data
    sea_water_temp, sea_water_sal = load_woa_data(args.temp_file, args.sal_file)
    lon = sea_water_temp.lon
    lat = sea_water_temp.lat
    depth = sea_water_temp.depth

    # Compute 3D Pressure
    pressure_3d = compute_pressure(depth, lat, lon)

    # Compute Stratification
    N_3D, depth_mid = compute_stratification(
        sea_water_temp, sea_water_sal, pressure_3d, lat
    )

    # Compute average N (bottom-X or full column)
    N_3D_ave = compute_bottom_average(
        N_3D, depth_mid, sea_water_temp, depth, args.depth_threshold
    )

    # Regrid the averaged field onto the original grid
    Nbot_data = regrid_data(N_3D_ave, lon, lat)

    # Add metadata
    this_file = os.path.normpath(__file__)
    runcmd = (
        f"python3 {os.path.basename(this_file)} "
        f"--temp-file={args.temp_file} "
        f"--sal-file={args.sal_file} "
        f"--depth-threshold={args.depth_threshold} "
        f"--output={args.output}"
    )

    global_attrs = {"history": get_provenance_metadata(this_file, runcmd)}
    Nbot_data.attrs.update(global_attrs)

    # Write output to a NetCDF file.
    Nbot_data.to_netcdf(args.output)


if __name__ == "__main__":
    main()
