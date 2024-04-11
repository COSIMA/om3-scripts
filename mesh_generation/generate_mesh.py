# Copyright 2023 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# =========================================================================================
# Generate an ESMF mesh file from an input grid.
#
# To run:
#   python generate_mesh.py --grid_type=<gridtype> --grid_filename=<grid_file> \
#     --mask_filename=<mask_file> --mesh_filename=<output_file>
#
# This script currently supports two grid_types:
#   - "mom" to generate a mesh representation of h-cells from a MOM supergrid
#   - "latlon" to generate a mesh representation from lat/lon locations
# For more information, run `python generate_mesh.py -h`
#
# The run command and full github url of the current version of this script is added to the
# metadata of the generated mesh file. This is to uniquely identify the script and inputs used
# to generate the mesh file. To produce mesh files for sharing, ensure you are using a version
# of this script which is committed and pushed to github. For mesh files intended for released
# configurations, use the latest version checked in to the main branch of the github repository.
#
# Contact:
#   Dougie Squire <dougal.squire@anu.edu.au>
#
# Dependencies:
#   argparse, xarray, numpy and pandas
# =========================================================================================

import os
import io
import hashlib
import warnings
import subprocess
from datetime import datetime

import numpy as np
import xarray as xr
import pandas as pd


def get_git_url(file):
    """
    If the provided file is in a git repo, return the url to its most recent commit remote.origin.
    """
    dirname = os.path.dirname(file)

    try:
        url = subprocess.check_output(
            ["git", "-C", dirname, "config", "--get", "remote.origin.url"]
        ).decode("ascii").strip()
        url = url.removesuffix('.git')
    except subprocess.CalledProcessError:
        return None

    if url.startswith("git@github.com:"):
        url = f"https://github.com/{url.removeprefix('git@github.com:')}"

    top_level_dir = subprocess.check_output(
        ["git", "-C", dirname, "rev-parse", "--show-toplevel"]
    ).decode("ascii").strip()
    rel_path = file.removeprefix(top_level_dir)

    hash = subprocess.check_output(
        ["git", "-C", dirname, "rev-parse", "HEAD"]
    ).decode("ascii").strip()

    return f"{url}/blob/{hash}{rel_path}"

def git_status(file):
    """
    Return the git status of the file. Returns:
    - "unstaged" if the file has unstaged changes
    - "uncommitted" if the file has uncommited changes,
    - "unpushed" if the repo has unpushed commits
    - None otherwise
    """
    dirname = os.path.dirname(file)
    status = subprocess.check_output(
        ["git", "-C", dirname, "status", file]
    ).decode("ascii").strip()

    if "Changes not staged for commit" in status:
        return "unstaged"
    elif "Changes to be committed" in status:
        return "uncommitted"
    elif "Your branch is ahead" in status:
        return "unpushed"
    else:
        return None

def md5sum(path):
    """
    Return the md5 hash of a provided file, reading in chunks to reduce memory usage for
    large files.
    From https://stackoverflow.com/a/40961519
    """
    length = io.DEFAULT_BUFFER_SIZE
    md5 = hashlib.md5()
    with io.open(path, mode="rb") as fd:
        for chunk in iter(lambda: fd.read(length), b''):
            md5.update(chunk)
    return md5.hexdigest()

class BaseGrid:

    def __init__(self, x_centres, y_centres, x_corners, y_corners, area=None, mask=None, inputs=None):
        """
        Initialise a mesh object

        Parameters
        ----------
        x_centres: len(elementCount) array-like
            Longitudinal positions of the element centre coords
        y_centres: len(elementCount) array-like
            Latitudinal positions of the element centre coords
        x_corners: (elementCount x 4) array-like
            Longitudinal positions of the corner nodes of each element, ordered ll, lr, ur, ul
        y_corners: (elementCount x 4) array-like
            LongitLatitudinaludinal positions of the corner nodes of each element, ordered ll, lr, ur, ul
        area: len(elementCount) array-like, optional
            Areas of each element
        mask: len(elementCount) array-like
            Mask values for each element, optional
        inputs: str or list of str, optional
            Paths to the files used to create the grid
        """

        self.x_centres = x_centres
        self.y_centres = y_centres

        self.x_corners = x_corners.flatten()
        self.y_corners = y_corners.flatten()

        self.area = area
        self.mask = mask

        if isinstance(inputs, str):
            inputs = [inputs]
        self.inputs = inputs

        self.mesh = None

    def create_mesh(self, wrap_lons=False, global_attrs=None):
        """
        Create the mesh as an xarray Dataset

        Parameters
        ----------
        wrap_lons: boolean, optional
            If True, wrap longitude values into the range between 0 and 360
        global_attrs: dict
            Global attributes to the mesh object
        """

        if wrap_lons:
            self.x_centres = (self.x_centres + 360) % 360
            self.x_corners = (self.x_corners + 360) % 360

        centres = np.stack((self.x_centres, self.y_centres), axis=1)
        corners_df = pd.DataFrame({"x": self.x_corners, "y": self.y_corners})

        # calculate indexes of corner nodes per element
        elem_conn = (
            corners_df.groupby(['x','y'], sort=False).ngroup()+1
        ).to_numpy().reshape((-1,4))

        # calculate corner nodes
        nodes = corners_df.drop_duplicates().to_numpy()

        # create mask if we don't have one
        if self.mask is None:
            self.mask = np.ones_like(self.x_centres, dtype=np.int8)

        # create a new dataset for the mesh
        ds = xr.Dataset()
        ds['nodeCoords'] = xr.DataArray(
            nodes.astype(np.float64),
            dims=('nodeCount', 'coordDim'),
            attrs={'units': 'degrees'}
        )
        ds['elementConn'] = xr.DataArray(
            elem_conn.astype(np.int32),
            dims=('elementCount', 'maxNodePElement'),
            attrs={'long_name': 'Node indices that define the element connectivity'}
        )
        ds['numElementConn'] = xr.DataArray(
            4 * np.ones_like(self.x_centres, dtype=np.int32),
            dims=('elementCount'),
            attrs={'long_name': 'Number of nodes per element'}
        )
        ds['centerCoords'] = xr.DataArray(
            centres.astype(np.float64),
            dims=('elementCount', 'coordDim'),
            attrs={'units': 'degrees'}
        )

        ds["elementMask"] = xr.DataArray(
            self.mask.astype(np.int8),
            dims=('elementCount'),
        )

        if self.area is not None:
            ds["elementArea"] = xr.DataArray(
                self.area.astype(np.float64),
                dims=('elementCount'),
            )

        # force no _FillValue (for now)
        for v in ds.variables:
            if '_FillValue' not in ds[v].encoding:
                ds[v].encoding['_FillValue'] = None

        # add global attributes
        ds.attrs = {
            "gridType" : "unstructured mesh",
            "timeGenerated": f"{datetime.now()}",
            "created_by": f"{os.environ.get('USER')}"
        }
        if self.inputs:
            file_hashes = []
            for input in self.inputs:
                file_hashes.append(f"{input} (md5 hash: {md5sum(input)})")
            ds.attrs["inputFile"] = ", ".join(file_hashes)

        # add git info to history
        if global_attrs:
            ds.attrs |= global_attrs

        self.mesh = ds

        return self

    def write(self, filename):
        """
        Save the mesh to a file
        """

        if self.mesh is None:
            raise ValueError("Before writing, you must first create the mesh object using self.create_mesh()")

        self.mesh.to_netcdf(filename)


class MomSuperGrid(BaseGrid):

    def __init__(self, hgrid_filename, mask_filename=None):
        """
        Initialise a mesh representation of h-cells from a MOM supergrid

        Parameters
        ----------
        hgrid_filename: str
            Path to the MOM hgrid netcdf file
        mask_filename: str, optional
            Path to a netcdf file containing a mask corresponding to the MOM hgrid
        """

        grid = xr.open_dataset(hgrid_filename)
        inputs = [hgrid_filename]

        if mask_filename:
            mask = xr.open_dataset(mask_filename).mask.values.flatten()
            inputs += [mask_filename]
        else:
            mask = None

        # sum areas in elements
        area = grid.area.values
        area = (
            area[::2, ::2] + area[1::2, ::2] + area[1::2, 1::2] + area[::2, 1::2]
        ).flatten()

        x = grid.x.values
        y = grid.y.values

        # prep x corners
        ll = x[:-2:2, :-2:2]
        lr = x[:-2:2, 2::2]
        ul = x[2::2, :-2:2]
        ur = x[2::2, 2::2]
        x_corners = np.stack((ll.flatten(), lr.flatten(), ur.flatten(), ul.flatten()), axis=1)
        x_centres = x[1:-1:2, 1:-1:2].flatten()

        # prep y corners
        ll = y[:-2:2, :-2:2]
        lr = y[:-2:2, 2::2]
        ul = y[2::2, :-2:2]
        ur = y[2::2, 2::2]
        y_corners = np.stack((ll.flatten(), lr.flatten(), ur.flatten(), ul.flatten()), axis=1)
        y_centres = y[1:-1:2, 1:-1:2].flatten()

        super().__init__(
            x_centres=x_centres,
            y_centres=y_centres,
            x_corners=x_corners,
            y_corners=y_corners,
            area=area,
            mask=mask,
            inputs=inputs,
        )


class LatLonGrid(BaseGrid):

    def __init__(self, grid_filename, mask_filename=None, lon_dim="lon", lat_dim="lat", area_var="area"):
        """
        Initialise a mesh representation from lat/lon locations

        Parameters
        ----------
        grid_filename: str
            Path to a netcdf file containing a lat/lon grid
        mask_filename: str, optional
            Path to a netcdf file containing a mask corresponding to the lat/lon grid
        lon_dim: str, optional
            The name of the longitude dimension
        lat_dim: str, optional
            The name of the latitude dimension
        area_var: str, optional
            The name of the area variable if one exists
        """

        grid = xr.open_dataset(grid_filename, chunks=-1)
        inputs = [grid_filename]

        if mask_filename:
            mask = xr.open_dataset(mask_filename).values.flatten()
            inputs += [mask_filename]
        else:
            mask = None

        if area_var in grid:
            area = grid[area_var].values.flatten()
        else:
            area = None

        x_centres = grid[lon_dim].values
        y_centres = grid[lat_dim].values

        has_lon_bounds = hasattr(grid[lon_dim], "bounds") and grid[lon_dim].bounds in grid
        has_lat_bounds = hasattr(grid[lat_dim], "bounds") and grid[lat_dim].bounds in grid

        if has_lon_bounds:
            lon_bnds = grid[getattr(grid[lon_dim], "bounds")]

            # flip and concat for ll, lr, ur, ul
            x_corners = np.concatenate([lon_bnds.values, lon_bnds[...,::-1].values], axis=-1)
        else:
            # Average neighbouring cells to get bounds
            ext = np.pad(x_centres, (1,),  mode='reflect', reflect_type='odd')
            bnds = (ext[:-1] + ext[1:]) / 2

            # stack as ll, lr, ur, ul
            x_corners = np.stack([bnds[:-1], bnds[1:], bnds[1:], bnds[:-1]], axis=1)

        if has_lat_bounds:
            lat_bnds = grid[getattr(grid[lat_dim], "bounds")]
            # repeat for ll, lr, ur, ul
            y_corners = np.repeat(lat_bnds.values, 2, axis=1)
        else:
            # Average neighbouring cells to get bounds
            ext = np.pad(y_centres, (1,),  mode='reflect', reflect_type='odd')
            bnds = (ext[:-1] + ext[1:]) / 2

            # stack as ll, lr, ur, ul
            y_corners = np.stack([bnds[:-1], bnds[:-1], bnds[1:], bnds[1:]], axis=1)

        # broadcast corners
        x_corners, y_corners = np.broadcast_arrays(
            np.expand_dims(x_corners, axis=0),
            np.expand_dims(y_corners, axis=1)
        )
        x_corners = x_corners.reshape(-1, 4)
        y_corners = y_corners.reshape(-1, 4)

        # broadcast centres
        x_centres, y_centres = np.broadcast_arrays(
            np.expand_dims(x_centres, axis=0),
            np.expand_dims(y_centres, axis=1)
        )
        x_centres = x_centres.flatten()
        y_centres = y_centres.flatten()

        super().__init__(
            x_centres=x_centres,
            y_centres=y_centres,
            x_corners=x_corners,
            y_corners=y_corners,
            area=area,
            mask=mask,
            inputs=inputs,
        )

gridtype_dispatch = {
    "latlon": LatLonGrid,
    "mom": MomSuperGrid,
}

def main():
    parser = argparse.ArgumentParser(
        description="Create an ESMF mesh file from a grid in a netcdf file."
    )

    parser.add_argument(
        "--grid-type",
        choices=gridtype_dispatch.keys(),
        required=True,
        help='The type of grid in the netcdf file.',
    )
    parser.add_argument(
        "--wrap-lons",
        default=False,
        action="store_true",
        help="Wrap longitude values into the range between 0 and 360."
    )
    parser.add_argument(
        "--grid-filename",
        type=str,
        required=True,
        help="The path to the netcdf file specifying the grid.",
    )
    parser.add_argument(
        "--mask-filename",
        type=str,
        default=None,
        help="The path to a netcdf file specifying the mask. If not passed, no mask is set in the mesh.",
    )
    parser.add_argument(
        "--mesh-filename",
        type=str,
        required=True,
        help="The path to the mesh file to create.",
    )

    args = parser.parse_args()
    grid_type = args.grid_type
    wrap_lons = args.wrap_lons
    grid_filename = os.path.abspath(args.grid_filename)
    mesh_filename = os.path.abspath(args.mesh_filename)
    mask_filename = args.mask_filename

    if mask_filename:
        mask_filename = os.path.abspath(mask_filename)

    this_file = os.path.normpath(__file__)

    # Add some info about how the file was generated
    runcmd = (
        f"python3 {os.path.basename(this_file)} --grid-type={grid_type} --grid-filename={grid_filename} "
        f"--mesh-filename={mesh_filename}"
    )
    if mask_filename:
        runcmd += f" --mask-filename={mask_filename}"
    if wrap_lons:
        runcmd += f" --wrap-lons"

    git_url = get_git_url(this_file)

    if git_url:
        status = git_status(this_file)
        if status in ["unstaged", "uncommitted"]:
            warnings.warn(f"{this_file} contains uncommitted changes! Commit and push your changes before generating any production output.")
        if status == "unpushed":
            warnings.warn(f"There are commits that are not pushed! Push your changes before generating any production output.")
        prepend = f"Created using {git_url}: "
    else:
        prepend = f"Created using {this_file}: "

    global_attrs = {"history": prepend + runcmd}

    mesh = gridtype_dispatch[grid_type](grid_filename, mask_filename)

    mesh.create_mesh(wrap_lons=wrap_lons, global_attrs=global_attrs).write(mesh_filename)

if __name__ == "__main__":
    import argparse

    main()
