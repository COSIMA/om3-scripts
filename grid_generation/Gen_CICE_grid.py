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

def generate_cice_grid(in_superGridPath, output_file):
    # Read input files
    in_superGridFile = xr.open_dataset(in_superGridPath)

    # Constants
    ULAT = np.deg2rad(in_superGridFile['y'][2::2, 2::2])
    ULON = np.deg2rad(in_superGridFile['x'][2::2, 2::2])
    TLAT = np.deg2rad(in_superGridFile['y'][1::2, 1::2])
    TLON = np.deg2rad(in_superGridFile['x'][1::2, 1::2])

    # MPI
    HTN = in_superGridFile['dx'] * 100.0  # convert to cm
    HTN = HTN[1::2, ::2] + HTN[1::2, 1::2]
    HTE = in_superGridFile['dy'] * 100.0  # convert to cm
    HTE = HTE[::2, 1::2] + HTE[1::2, 1::2]

    ANGLE = np.deg2rad(in_superGridFile['angle_dx'][2::2, 2::2])
    ANGLET= np.deg2rad(in_superGridFile['angle_dx'][1::2, 1::2])
       
    # Area
    AREA  = (in_superGridFile['area'])
    TAREA = AREA[::2,::2] + AREA[1::2,1::2] + AREA[::2,1::2] +  AREA[1::2,::2]
    
    array_to_roll = AREA[2::2,2::2]
    
    # Roll the array along axis 0 and concatenate the last row as the first row
    rolled_array_axis0 = np.concatenate((
    np.roll(array_to_roll, -1, axis=0),
    array_to_roll[-1:, :]), axis=0)

    # Roll the rolled array along axis 1 and concatenate the last column as the first column
    rolled_array = np.concatenate((
    np.roll(rolled_array_axis0, -1, axis=1),
    rolled_array_axis0[:, -1:]), axis=1)
    
    UAREA = AREA[1::2,1::2] + np.concatenate((np.roll(AREA[1::2, 2::2], -1, axis=1), AREA[1::2, 2::2][:, :1]), axis=1) + np.concatenate((np.roll(AREA[2::2, 1::2], -1, axis=0), AREA[2::2, 1::2][:1, :]), axis=0) + rolled_array

    # Close input files
    in_superGridFile.close()

    # Create a new NetCDF file
    nc = Dataset(output_file, 'w', format='NETCDF4')

    # Define dimensions
    ny, nx = ULAT.shape
    nc.createDimension('ny', ny)
    nc.createDimension('nx', nx)

    # Define variables
    ulat = nc.createVariable('ulat', 'f8', ('ny', 'nx'))
    ulon = nc.createVariable('ulon', 'f8', ('ny', 'nx'))
    tlat = nc.createVariable('tlat', 'f8', ('ny', 'nx'))
    tlon = nc.createVariable('tlon', 'f8', ('ny', 'nx'))
    htn = nc.createVariable('htn', 'f8', ('ny', 'nx'))
    hte = nc.createVariable('hte', 'f8', ('ny', 'nx'))
    angle = nc.createVariable('angle', 'f8', ('ny', 'nx'))
    angleT = nc.createVariable('angleT', 'f8', ('ny', 'nx'))
    tarea = nc.createVariable('tarea', 'f8', ('ny', 'nx'))
    uarea = nc.createVariable('uarea', 'f8', ('ny', 'nx'))

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
