#!/usr/bin/env python3
# Copyright 2023 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0

# Generate a datm xml file that contains a time-series of input atmosphere data files where all the fields in the stream are located.

# To run:
#   python generate_xml_datm.py <year_first> <year_last>
# To generate IAF xml file, set year_first and year_last to the forcing period
# To generate RYF xml file, set year_first==year_last


# Contact: Ezhilsabareesh Kannadasan <ezhilsabareesh.kannadasan@anu.edu.au>

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import sys
from datetime import datetime
from pathlib import Path

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from scripts_common import get_provenance_metadata

if len(sys.argv) != 3:
    print("Usage: python generate_xml_datm.py year_first year_last")
    sys.exit(1)

try:
    year_first = int(sys.argv[1])
    year_last = int(sys.argv[2])

except ValueError:
    print("Year values must be integers")
    sys.exit(1)

year_align = year_first

# Create the root element
root = Element("file", id="stream", version="2.0")

# Obtain metadata
this_file = sys.argv[0]
runcmd = " ".join(sys.argv)
metadata_info = get_provenance_metadata(this_file, runcmd)

# Add metadata
metadata = SubElement(root, "metadata")
SubElement(metadata, "File_type").text = "DATM xml file provides forcing data"
SubElement(metadata, "date_generated").text = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)
SubElement(metadata, "history").text = metadata_info

# Define the stream info names and corresponding var names
stream_info_names = [
    "CORE_IAF_JRA55do.PRSN",
    "CORE_IAF_JRA55do.PRRN",
    "CORE_IAF_JRA55do.LWDN",
    "CORE_IAF_JRA55do.SWDN",
    "CORE_IAF_JRA55do.Q_10",
    "CORE_IAF_JRA55do.SLP_10",
    "CORE_IAF_JRA55do.T_10",
    "CORE_IAF_JRA55do.U_10",
    "CORE_IAF_JRA55do.V_10",
]

var_names = {
    "CORE_IAF_JRA55do.PRSN": ("prsn", "Faxa_prsn"),
    "CORE_IAF_JRA55do.PRRN": ("prra", "Faxa_prrn"),
    "CORE_IAF_JRA55do.LWDN": ("rlds", "Faxa_lwdn"),
    "CORE_IAF_JRA55do.SWDN": ("rsds", "Faxa_swdn"),
    "CORE_IAF_JRA55do.Q_10": ("huss", "Sa_shum"),
    "CORE_IAF_JRA55do.SLP_10": ("psl", "Sa_pslv"),
    "CORE_IAF_JRA55do.T_10": ("tas", "Sa_tbot"),
    "CORE_IAF_JRA55do.U_10": ("uas", "Sa_u"),
    "CORE_IAF_JRA55do.V_10": ("vas", "Sa_v"),
}

# Generate stream info elements with changing years
for stream_name in stream_info_names:
    stream_info = SubElement(root, "stream_info", name=stream_name)
    if year_first == year_last:
        SubElement(stream_info, "taxmode").text = "cycle"
    else:
        SubElement(stream_info, "taxmode").text = "limit"
    SubElement(stream_info, "readmode").text = "single"
    SubElement(stream_info, "mapalgo").text = "bilinear"
    SubElement(stream_info, "dtlimit").text = "1.5"
    SubElement(stream_info, "year_first").text = str(year_first)
    SubElement(stream_info, "year_last").text = str(year_last)
    SubElement(stream_info, "year_align").text = str(year_align)
    SubElement(stream_info, "vectors").text = "null"
    SubElement(stream_info, "meshfile").text = "./INPUT/JRA55do-ESMFmesh.nc"
    SubElement(stream_info, "lev_dimname").text = "null"

    datafiles = SubElement(stream_info, "datafiles")
    datavars = SubElement(stream_info, "datavars")

    if stream_name in (
        [
            "CORE_IAF_JRA55do.PRSN",
            "CORE_IAF_JRA55do.PRRN",
            "CORE_IAF_JRA55do.LWDN",
            "CORE_IAF_JRA55do.SWDN",
        ]
    ) and (year_first != year_last):
        SubElement(stream_info, "offset").text = (
            "-5400"  # shift back 1.5hr to match RYF
        )
    else:
        SubElement(stream_info, "offset").text = "0"

    var_name_parts = var_names.get(
        stream_name,
        (
            stream_name.split(".")[-1].lower(),
            f"Faxa_{stream_name.split('.')[-1].lower()}",
        ),
    )
    var_element = SubElement(datavars, "var")
    var_element.text = f"{var_name_parts[0]}  {var_name_parts[1]}"

    if stream_name == "CORE_IAF_JRA55do.SWDN":
        SubElement(stream_info, "tintalgo").text = "coszen"
    else:
        SubElement(stream_info, "tintalgo").text = "linear"

    for year in range(year_first, year_last + 1):
        if year_first == year_last:
            file_element = SubElement(datafiles, "file")
            file_element.text = (
                f"./INPUT/RYF.{var_name_parts[0]}.{year+90}_{year + 90 + 1}.nc"
            )
        else:
            file_element = SubElement(datafiles, "file")
            if stream_name not in [
                "CORE_IAF_JRA55do.SLP_10",
                "CORE_IAF_JRA55do.T_10",
                "CORE_IAF_JRA55do.Q_10",
                "CORE_IAF_JRA55do.U_10",
                "CORE_IAF_JRA55do.V_10",
            ]:
                if year != 2019:
                    file_element.text = f"./INPUT/atmos/3hr/{var_name_parts[0]}/gr/v20190429/{var_name_parts[0]}_input4MIPs_atmosphericState_OMIP_MRI-JRA55-do-1-4-0_gr_{year}01010130-{year}12312230.nc"
                else:
                    file_element.text = f"./INPUT/atmos/3hr/{var_name_parts[0]}/gr/v20190429/{var_name_parts[0]}_input4MIPs_atmosphericState_OMIP_MRI-JRA55-do-1-4-0_gr_{year}01010130-{year}01052230.nc"
            else:
                if year != 2019:
                    file_element.text = f"./INPUT/atmos/3hrPt/{var_name_parts[0]}/gr/v20190429/{var_name_parts[0]}_input4MIPs_atmosphericState_OMIP_MRI-JRA55-do-1-4-0_gr_{year}01010000-{year}12312100.nc"
                else:
                    file_element.text = f"./INPUT/atmos/3hrPt/{var_name_parts[0]}/gr/v20190429/{var_name_parts[0]}_input4MIPs_atmosphericState_OMIP_MRI-JRA55-do-1-4-0_gr_{year}01010000-{year}01052100.nc"


# Convert the XML to a nicely formatted string
xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")

# Write the XML content to a file
with open("datm.streams.xml", "w") as xml_file:
    xml_file.write(xml_str)
