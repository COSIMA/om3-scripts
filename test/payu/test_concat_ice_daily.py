import pytest
import xarray as xr
import numpy as np
import pandas as pd

from os import makedirs, chdir
from subprocess import run
from pathlib import Path


def assertIsFile(path):
    if not Path(path).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(path))


@pytest.fixture
def daily_files(tmp_path):
    """
    Make 365 days of fake data, and then write it into 365 files
    """

    nx = 30
    ny = 50
    nt = 365

    da = xr.DataArray(
        np.random.rand(nx, ny, nt),
        dims=["x", "y", "time"],
        coords={"time": pd.date_range("2010-01-01", freq="D", periods=nt)},
    )
    ds = da.to_dataset(name="aice")

    out_dir = f"{tmp_path}/archive/output000/"
    paths = [f"{out_dir}access-om3.cice.h.{str(t.values)[0:10]}.nc" for t in ds.time]
    datasets = [ds.sel(time=slice(t, t)) for t in ds.time]

    makedirs(out_dir)
    xr.save_mfdataset(datasets, paths, unlimited_dims=["time"])

    return out_dir


def test_concat_ice(daily_files, tmp_path):
    """
    Run the script to convert the daily data into monthly files, and check the files exist.
    """

    chdir(tmp_path)

    scripts_base = Path(__file__).parents[2]
    run([f"{scripts_base}/payu/archive_scripts/concat_ice_daily.sh"])

    expected_months = pd.date_range("2010-01-01", freq="ME", periods=12)

    monthly_paths = [
        f"{daily_files}access-om3.cice.h.day.{str(t)[0:7]}.nc" for t in expected_months
    ]

    for p in monthly_paths:
        assertIsFile(p)
