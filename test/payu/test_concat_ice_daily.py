import pytest
import xarray as xr
import numpy as np
import pandas as pd

from os import makedirs, chdir
from subprocess import run
from pathlib import Path


def assert_file_exists(p):
    if not Path(p).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(p))


def assert_f_not_exists(p):
    if Path(p).resolve().is_file():
        raise AssertionError("File exists and should not: %s" % str(p))


@pytest.fixture
def daily_files(request, tmp_path):
    """
    Make 365 days of fake data, and then write it into 365 files

    request = (path, ndays)
    e.g. request = ("archive/output000", "365")

    """

    if request.param[0] == "Default":
        dir_name = "archive/output000"
    else:
        dir_name = str(request.param[0])

    ndays = request.param[1]

    nx = 30
    ny = 50

    da = xr.DataArray(
        np.random.rand(ndays, nx, ny),
        dims=[
            "time",
            "x",
            "y",
        ],  # there is a bug in nco that means time needs to be the first dimension!
        coords={"time": pd.date_range("2010-01-01 12:00", freq="D", periods=ndays)},
    )
    ds = da.to_dataset(name="aice")

    # Setting these would be more like the source data, but maybe it doesn't matter!
    # ds.time.encoding['units'] = 'Days since 01/01/2000 00:00:00 UTC'
    # ds.time.encoding['calendar'] = 'gregorian'
    # ds.time.encoding['dtype'] = 'float'

    out_dir = str(tmp_path) + "/" + dir_name + "/"
    paths = [f"{out_dir}access-om3.cice.h.{str(t.values)[0:10]}.nc" for t in ds.time]
    datasets = [ds.sel(time=slice(t, t)) for t in ds.time]

    makedirs(out_dir)
    xr.save_mfdataset(datasets, paths, unlimited_dims=["time"])

    return paths


@pytest.mark.parametrize(
    "daily_files, use_dir, nmonths",
    [
        (("archive/output000", 365), False, 12),
        (("archive/output999", 31), False, 1),
        (("archive/output9999", 31), False, 1),
        (("archive/output574", 365), True, 12),
    ],
    indirect=["daily_files"],
)  # run this test with a several folder names and lengths, provide the directory as an argument sometimes
def test_true_case(daily_files, use_dir, nmonths, tmp_path):
    """
    Run the script to convert the daily data into monthly files, and check the monthly files and the daily files dont exist.
    """

    chdir(tmp_path)
    output_dir = Path(daily_files[0]).parents[0]
    scripts_base = Path(__file__).parents[2]

    if not use_dir:  # default path
        run([f"{scripts_base}/payu/archive_scripts/concat_ice_daily.sh"])
        expected_months = pd.date_range("2010-01-01", freq="ME", periods=nmonths + 1)
    else:  # provide path
        run(
            [
                f"{scripts_base}/payu/archive_scripts/concat_ice_daily.sh",
                "-d",
                output_dir,
            ]
        )
        expected_months = pd.date_range("2010-01-01", freq="ME", periods=nmonths + 1)

    # valid output filenames
    monthly_paths = [
        f"{output_dir}/access-om3.cice.h.day.{str(t)[0:7]}.nc" for t in expected_months
    ]

    for p in monthly_paths[0:nmonths]:
        assert_file_exists(p)

    for p in monthly_paths[nmonths]:
        assert_f_not_exists(p)

    for p in daily_files:
        assert_f_not_exists(p)


@pytest.mark.parametrize(
    "daily_files", [("Default", 1), ("Default", 27)], indirect=True
)
def test_no_concat_case(daily_files, tmp_path):
    """
    Run the script to convert the daily data into monthly files, with less than 28 days data, and check no things happen.
    """

    chdir(tmp_path)
    output_dir = Path(daily_files[0]).parents[0]

    scripts_base = Path(__file__).parents[2]
    run([f"{scripts_base}/payu/archive_scripts/concat_ice_daily.sh"])
    expected_months = pd.date_range("2010-01-01", freq="ME", periods=1)

    monthly_paths = [
        f"{output_dir}/access-om3.cice.h.day.{str(t)[0:7]}.nc" for t in expected_months
    ]

    for p in daily_files:
        assert_file_exists(p)

    for p in monthly_paths:
        assert_f_not_exists(p)
