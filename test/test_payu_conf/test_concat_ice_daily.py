import pytest
import xarray as xr
import numpy as np
import pandas as pd

from os import makedirs, chdir
from subprocess import run
from pathlib import Path

scripts_base = Path(__file__).parents[2]
run_str = f"{scripts_base}/payu_config/archive_scripts/concat_ice_daily.sh"


def assert_file_exists(p):
    if not Path(p).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(p))


def assert_f_not_exists(p):
    if Path(p).resolve().is_file():
        raise AssertionError("File exists and should not: %s" % str(p))


def daily_files(dir_name, hist_base, ndays, tmp_path):
    """
    Make 365 days of fake data, and then write it into 365 files

    request = (path, ndays)
    e.g. request = ("archive/output000", "365")

    """

    if dir_name == "Default":
        dir_name = "archive/output000"

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
    paths = [f"{out_dir}{hist_base}.{str(t.values)[0:10]}.nc" for t in ds.time]
    datasets = [ds.sel(time=slice(t, t)) for t in ds.time]

    makedirs(out_dir)
    xr.save_mfdataset(datasets, paths, unlimited_dims=["time"])

    return paths


@pytest.fixture(
    params=["access-om3.cice.h", "access-om3.cice", "access-om3.cice.1day.mean"]
)
def hist_base(request):
    return str(request.param)


@pytest.mark.parametrize(
    "hist_dir, ndays, use_dir, nmonths",
    [
        ("archive/output000", 365, False, 12),
        ("archive/output999", 31, False, 1),
        ("archive/output9999", 31, False, 1),
        ("archive/output574", 365, True, 12),
    ],
)  # run this test with a several folder names and lengths, provide the directory as an argument sometimes
def test_true_case(hist_dir, ndays, use_dir, nmonths, hist_base, tmp_path):
    """
    Run the script to convert the daily data into monthly files, and check the monthly files and the daily files dont exist.
    """

    daily_paths = daily_files(hist_dir, hist_base, ndays, tmp_path)
    chdir(tmp_path)
    output_dir = Path(daily_paths[0]).parents[0]

    if not use_dir:  # default path
        result = run([run_str], capture_output=True)
        result.stdout
        result.stderr
        expected_months = pd.date_range("2010-01-01", freq="ME", periods=nmonths + 1)
    else:  # provide path
        result = run(
            [
                run_str,
                "-d",
                output_dir,
            ],
            capture_output=True,
        )
        result.stdout
        result.stderr
        expected_months = pd.date_range("2010-01-01", freq="ME", periods=nmonths + 1)

    # valid output filenames
    monthly_paths = [
        f"{output_dir}/{hist_base}.{str(t)[0:7]}.nc" for t in expected_months
    ]

    for p in monthly_paths[0:nmonths]:
        assert_file_exists(p)

    for p in monthly_paths[nmonths]:
        assert_f_not_exists(p)

    for p in daily_paths:
        assert_f_not_exists(p)


@pytest.mark.parametrize("hist_dir, ndays", [("Default", 1), ("Default", 30)])
def test_incomplete_month(hist_dir, ndays, hist_base, tmp_path):
    """
    Run the script to convert the daily data into monthly files, with less than 28 days data, and check no things happen.
    """

    daily_paths = daily_files(hist_dir, hist_base, ndays, tmp_path)

    chdir(tmp_path)
    output_dir = Path(daily_paths[0]).parents[0]

    run([run_str])
    expected_months = pd.date_range("2010-01-01", freq="ME", periods=1)

    monthly_paths = [
        f"{output_dir}/{hist_base}.{str(t)[0:7]}.nc" for t in expected_months
    ]

    for p in daily_paths:
        assert_file_exists(p)

    for p in monthly_paths:
        assert_f_not_exists(p)


@pytest.mark.parametrize("hist_dir, ndays", [("Default", 31), ("Default", 27)])
def test_no_override(hist_dir, ndays, hist_base, tmp_path):
    """
    Run the script to convert the daily data into monthly files, but the output filename already exists, and check nothing happens.
    """

    daily_paths = daily_files(hist_dir, hist_base, ndays, tmp_path)

    chdir(tmp_path)
    output_dir = Path(daily_paths[0]).parents[0]

    expected_months = pd.date_range("2010-01-01", freq="ME", periods=1)

    monthly_paths = [
        f"{output_dir}/{hist_base}.{str(t)[0:7]}.nc" for t in expected_months
    ]
    for p in monthly_paths:
        Path(p).touch()

    run([run_str])

    for p in daily_paths:
        assert_file_exists(p)

    for p in monthly_paths:
        assert_file_exists(p)
