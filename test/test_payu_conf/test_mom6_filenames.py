import pytest
import xarray as xr
import numpy as np
import pandas as pd

from os import makedirs, chdir
from subprocess import run
from pathlib import Path

scripts_base = Path(__file__).parents[2]
run_str = f"{scripts_base}/payu_config/archive_scripts/standardise_mom6_filenames.sh"


def assert_file_exists(p):
    if not Path(p).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(p))


def assert_f_not_exists(p):
    if Path(p).resolve().is_file():
        raise AssertionError("File exists and should not: %s" % str(p))


def monthly_files(dir_name, hist_base, nmonths, tmp_path):
    """
    Make 12 months of empty data files data, and then write it into 12 files

    request = (path, ndays)
    e.g. request = ("archive/output000", "365")

    """

    times = pd.date_range("2010-01-01 12:00", freq="ME", periods=nmonths+1)

    out_dir = str(tmp_path) + "/" + dir_name + "/"
    paths = [f"{out_dir}{hist_base}_{str(t)[0:7]}.nc" for t in times]
    
    makedirs(out_dir)

    for path in paths:
        with open(path, "w") as f:
            f.close()

    return paths


@pytest.fixture(
    params=["access-om3.mom.h.test"] #, "access-om3.cice", "access-om3.cice.1day.mean"]
)
def hist_base(request):
    return str(request.param)


@pytest.mark.parametrize(
    "hist_dir, use_dir, nmonths",
    [
        ("Default", False, 12),
        ("archive/output999", False, 1),
        ("archive/output9999", False, 1),
        ("archive/output574", True, 12),
    ],
)  # run this test with a several folder names and lengths, provide the directory as an argument sometimes
def test_true_case(hist_dir, use_dir, nmonths, hist_base, tmp_path):


    monthly_paths = monthly_files(hist_dir, hist_base, nmonths, tmp_path)
    chdir(tmp_path)
    output_dir = Path(monthly_paths[0]).parents[0]

    if not use_dir:  # default path
        run([run_str])
        expected_months = pd.date_range("2010-01-01", freq="ME", periods=nmonths + 1)
    else:  # provide path
        run(
            [
                run_str,
                "-d",
                output_dir,
            ],
        )
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


# @pytest.mark.parametrize("hist_dir, ndays", [("Default", 1), ("Default", 30)])
# def test_incomplete_month(hist_dir, ndays, hist_base, tmp_path):
#     """
#     Run the script to convert the daily data into monthly files, with less than 28 days data, and check no things happen.
#     """

#     daily_paths = daily_files(hist_dir, hist_base, ndays, tmp_path)

#     chdir(tmp_path)
#     output_dir = Path(daily_paths[0]).parents[0]

#     run([run_str])
#     expected_months = pd.date_range("2010-01-01", freq="ME", periods=1)

#     monthly_paths = [
#         f"{output_dir}/{hist_base}.{str(t)[0:7]}.nc" for t in expected_months
#     ]

#     for p in daily_paths:
#         assert_file_exists(p)

#     for p in monthly_paths:
#         assert_f_not_exists(p)


# @pytest.mark.parametrize("hist_dir, ndays", [("Default", 31), ("Default", 27)])
# def test_no_override(hist_dir, ndays, hist_base, tmp_path):
#     """
#     Run the script to convert the daily data into monthly files, but the output filename already exists, and check nothing happens.
#     """

#     daily_paths = daily_files(hist_dir, hist_base, ndays, tmp_path)

#     chdir(tmp_path)
#     output_dir = Path(daily_paths[0]).parents[0]

#     expected_months = pd.date_range("2010-01-01", freq="ME", periods=1)

#     monthly_paths = [
#         f"{output_dir}/{hist_base}.{str(t)[0:7]}.nc" for t in expected_months
#     ]
#     for p in monthly_paths:
#         Path(p).touch()

#     run([run_str])

#     for p in daily_paths:
#         assert_file_exists(p)

#     for p in monthly_paths:
#         assert_file_exists(p)
