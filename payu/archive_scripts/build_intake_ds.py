#!python3
# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
# modules:
# use:
#     - /g/data/xp65/public/modules
# load:
#     - conda/access-med-0.7

from dask.distributed import Client
from access_nri_intake.source import builders
from os import environ,getcwd

from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from tools.git import *
from tools.md5sum import *

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

METADATA_FILENAME = 'metadata.yaml'
UUID_FIELD = "experiment_uuid"

if __name__ == '__main__':
    # Start dask, with a max of 48 procs
    # inspired from https://climtas.readthedocs.io/en/latest/_modules/climtas/nci.html#Client
    workers = int(environ["PBS_NCPUS"])
    mem = int(environ["PBS_VMEM"]) / workers
    if workers > 48:
        workers = 48
    client = Client(
        n_workers=workers , 
        threads_per_worker=1, # per https://github.com/pydata/xarray/issues/7079 netcdf doesn't like threads
        memory_limit=mem
    )

    builder = builders.AccessOm3Builder(path="archive/") #TODO: make path an optional argument?

    builder.build()

    # Log invalid assets
    builder.invalid_assets

    # Get experiment uuid
    # follows https://github.com/payu-org/payu/blob/ef55e93fe23fcde19024479c0dc4112dcdf6603f/payu/metadata.py#L90
    metadata_filename = Path(METADATA_FILENAME)
    if metadata_filename.exists():
        metadata = CommentedMap()
        metadata = YAML().load(metadata_filename)
        uuid = metadata.get(UUID_FIELD, None)
    else:
        warn(f"{METADATA_FILENAME} not found in archive folder")

    # Check git status of this .py file
    this_file = os.path.normpath(__file__)
    created_using = get_created_str(this_file)

    # Save the datastore to a file (json)
    builder.save(
        name=f"intake_datastore_{uuid[0:8]}",
        description=f"intake_datastore for experiment {uuid}, in folder {getcwd()}. {created_using}. (md5 hash: {md5sum(this_file)})",
        directory="archive/",
    )

    client.close()
