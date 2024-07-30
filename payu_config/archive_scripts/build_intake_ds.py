#!python3
# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
# modules:
# use:
#     - /g/data/hh5/public/modules
# load:
#     - conda/analysis

from access_nri_intake.source import builders
from payu.metadata import Metadata
import os
import sys
from pathlib import Path

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum

METADATA_FILENAME = "metadata.yaml"
UUID_FIELD = "experiment_uuid"
ARCHIVE_PATH = "archive"


def description():
    # Get experiment uuid
    uuid = Metadata(laboratory_archive_path=ARCHIVE_PATH).uuid

    # Check git status of this .py file
    this_file = os.path.normpath(__file__)

    runcmd = f"python3 {os.path.basename(this_file)}"

    # Get string "Created using $file: $command"
    provenance = get_provenance_metadata(this_file, runcmd)

    if uuid:
        description = f"intake-esm datastore for experiment {uuid}, in folder {os.getcwd()}. {provenance}. (md5 hash: {md5sum(this_file)})"
    else:
        description = f"intake-esm datastore for experiment in folder {os.getcwd()}. {provenance}. (md5 hash: {md5sum(this_file)})"

    return description


if __name__ == "__main__":

    builder = builders.AccessOm3Builder(path="archive/")

    builder.build()

    # Log invalid assets
    builder.invalid_assets

    # Save the datastore to a file (json)
    builder.save(
        name=f"intake_esm_ds",
        description=description(),
        directory=ARCHIVE_PATH,
    )
