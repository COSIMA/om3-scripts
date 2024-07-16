#!python3
# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
# modules:
# use:
#     - /g/data/hh5/public/modules
# load:
#     - conda/analysis

from access_nri_intake.source import builders
from os import getcwd

from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata, md5sum

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

METADATA_FILENAME = "metadata.yaml"
UUID_FIELD = "experiment_uuid"

builder = builders.AccessOm3Builder(path="archive/")

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

runcmd = f"python3 {os.path.basename(this_file)}"

# Get string "Created using $file: $command"
provenance = get_provenance_metadata(this_file, runcmd)

# Save the datastore to a file (json)
builder.save(
    name=f"intake_datastore_{uuid[0:8]}",
    description=f"intake_datastore for experiment {uuid}, in folder {getcwd()}. {provenance}. (md5 hash: {md5sum(this_file)})",
    directory="archive/",
)
