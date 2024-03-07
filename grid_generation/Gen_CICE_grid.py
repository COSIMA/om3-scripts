"""
Script: Gen_CICE_grid.py

Description: 
This script generates a CICE grid from the MOM super grid provided in the input NetCDF file.

Contact: 
Name: Ezhilsabareesh Kannadasan

Usage:
python generate_cice_grid.py <input_superGridPath> <output_file>
- input_superGridPath: Path to the MOM super grid NetCDF file.
- output_file: Path to the output CICE grid NetCDF file.
"""
import numpy as np
import xarray as xr
from netCDF4 import Dataset
import sys
import os
import subprocess
from datetime import datetime


def is_git_repo():
    """
    Return True/False depending on whether or not the current directory is a git repo.
    """

    return subprocess.call(
        ['git', '-C', '.', 'status'],
        stderr=subprocess.STDOUT,
        stdout = open(os.devnull, 'w')
    ) == 0

def git_info():
    """
    Return the git repo origin url, relative path to this file, and latest commit hash.
    """

    url = subprocess.check_output(
        ["git", "remote", "get-url", "origin"]
    ).decode('ascii').strip()
    top_level_dir = subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel']
    ).decode('ascii').strip()
    rel_path = os.path.relpath(__file__, top_level_dir)
    hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']
    ).decode('ascii').strip()

    return url, rel_path, hash

def generate_cice_grid(in_superGridPath, output_file):
    # Read input files
    in_superGridFile = xr.open_dataset(in_superGridPath)

    # Constants
    ULAT = np.deg2rad(in_superGridFile['y'][2::2, 2::2])
    ULON = np.deg2rad(in_superGridFile['x'][2::2, 2::2])
    TLAT = np.deg2rad(in_superGridFile['y'][1::2, 1::2])
    TLON = np.deg2rad(in_superGridFile['x'][1::2, 1::2])

    HTN = in_superGridFile['dx'] * 100.0  # convert to cm
    HTN = HTN[2::2, ::2] + HTN[2::2, 1::2]
    HTE = in_superGridFile['dy'] * 100.0  # convert to cm
    HTE = HTE[::2, 2::2] + HTE[1::2, 2::2]

    # The angle of rotation is at corner cell centres and applies to both t and u cells.
    ANGLE = np.deg2rad(in_superGridFile['angle_dx'][2::2, 2::2])
    ANGLET= np.deg2rad(in_superGridFile['angle_dx'][1::2, 1::2])
       
    # Area
    AREA  = (in_superGridFile['area'])
    TAREA = AREA[::2,::2] + AREA[1::2,1::2] + AREA[::2,1::2] +  AREA[1::2,::2]
    
    # UAREA need to wrap around the globe. Copy ocn_area and
    # add an extra column at the end. Also u-cells cross the
    # tri-polar fold so add an extra row at the top.
    area_ext = np.append(AREA[:], AREA[:, 0:1], axis=1)
    area_ext = np.append(area_ext[:], area_ext[-1:, :], axis=0)

    UAREA = area_ext[1::2, 1::2] + area_ext[2::2, 1::2] + \
                area_ext[2::2, 2::2] + area_ext[1::2, 2::2]

    # Close input files
    in_superGridFile.close()

    # Create a new NetCDF file
    nc = Dataset(output_file, 'w', format='NETCDF4')

    # Define dimensions
    ny, nx = ULAT.shape
    nc.createDimension('ny', ny)
    nc.createDimension('nx', nx)

    # Define variables
    ulat = nc.createVariable('ulat', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    ulon = nc.createVariable('ulon', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    tlat = nc.createVariable('tlat', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    tlon = nc.createVariable('tlon', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    htn = nc.createVariable('htn', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    hte = nc.createVariable('hte', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    angle = nc.createVariable('angle', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    angleT = nc.createVariable('angleT', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    tarea = nc.createVariable('tarea', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)
    uarea = nc.createVariable('uarea', 'f8', ('ny', 'nx'), compression='zlib', complevel=1)

    # Add attributes
    ulat.units = "radians"
    ulat.title = "Latitude of U points"
    ulon.units = "radians"
    ulon.title = "Longitude of U points"
    tlat.units = "radians"
    tlat.title = "Latitude of T points"
    tlon.units = "radians"
    tlon.title = "Longitude of T points"
    htn.units = "cm"
    htn.title = "Width of T cells on N side."
    hte.units = "cm"
    hte.title = "Width of T cells on E side."
    angle.units = "radians"
    angle.title = "Rotation angle of U cells."
    angleT.units = "radians" 
    angleT.title = "Rotation angle of T cells." 
    tarea.units = "m^2" 
    tarea.title = "Area of T cells." 
    uarea.units = "m^2" 
    uarea.title = "Area of U cells." 

    # Add versioning information    
    if is_git_repo():
        git_url, git_hash, rel_path = git_info()
        nc.inputfile = f"{in_superGridPath}"
        nc.timeGenerated = f"{datetime.now()}"
        nc.created_by = f"{os.environ.get('USER')}"
        nc.history = f"Created using commit {git_hash} of {git_url}"
    else:
        nc.inputfile = f"{in_superGridPath}"
        nc.timeGenerated = f"{datetime.now()}"
        nc.created_by = f"{os.environ.get('USER')}"
        nc.history = f"python Gen_CICE_grid.py {in_superGridPath} {output_file}"

    # Write data to variables
    ulat[:] = ULAT
    ulon[:] = ULON
    tlat[:] = TLAT
    tlon[:] = TLON
    htn[:] = HTN
    hte[:] = HTE
    angle[:] = ANGLE
    angleT[:] = ANGLET
    tarea[:] = TAREA
    uarea[:] = UAREA
    # Close the file
    nc.close()

    print("NetCDF file created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Gen_CICE_grid.py <input_superGridPath> <output_file>")
        sys.exit(1)

    input_superGridPath = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_cice_grid(input_superGridPath, output_file)
