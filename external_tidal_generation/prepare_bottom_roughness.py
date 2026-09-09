#!/usr/bin/env python3
# Copyright 2026 ACCESS-NRI and contributors.
# SPDX-License-Identifier: Apache-2.0
#
# Check or generate the shared intermediate bottom roughness.
#

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from netCDF4 import Dataset

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts_common import get_provenance_input_files


GENERATOR = Path(__file__).resolve().parent / "generate_bottom_roughness_intermediate_woa.py"


def provenance(inputs):
    """
    Recreate the inputfile attribute written by get_provenance_metadata.
    """
    return get_provenance_input_files([str(path) for path in inputs])


def is_current(output, expected):
    if not output.is_file():
        return False
    with Dataset(output) as dataset:
        return dataset.getncattr("inputFile") == expected


def generate(output, inputs, expected):
    """
    Run the MPI calculation inside PBS, publishing only a complete result.
    """
    ncpus = os.environ.get("PBS_NCPUS")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".bottom-roughness-", dir=output.parent
    ) as directory:
        temporary = Path(directory) / output.name
        subprocess.run(
            [
                "mpirun",
                "-n",
                ncpus,
                sys.executable,
                str(GENERATOR),
                "--woa_temp_file",
                str(inputs[0]),
                "--woa_salt_file",
                str(inputs[1]),
                "--synbath_file",
                str(inputs[2]),
                "--woa_intermediate_file",
                str(temporary),
            ],
            check=True,
        )

        with Dataset(temporary) as dataset:
            generated = dataset.getncattr("inputFile")
        if generated != expected or provenance(inputs) != expected:
            raise RuntimeError("An input changed during generation; output not updated")

        os.replace(temporary, output)

    print(f"Updated {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--woa-temp-file", type=Path, required=True)
    parser.add_argument("--woa-salt-file", type=Path, required=True)
    parser.add_argument("--synbath-file", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        required=True
        )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return 0 when current and 1 when generation is needed",
        )
    args = parser.parse_args()

    inputs = [
        args.woa_temp_file.expanduser().resolve(),
        args.woa_salt_file.expanduser().resolve(),
        args.synbath_file.expanduser().resolve(),
    ]

    output = args.output.expanduser().resolve()
    expected = provenance(inputs)
    if is_current(output, expected):
        print(f"Reusing {output}")
        return 0
    if args.check:
        print(f"Intermediate needs generation: {output}")
        return 1

    generate(output, inputs, expected)
    return 0

if __name__ == "__main__":
    try:
        status = main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        status = 2

    sys.exit(status)
