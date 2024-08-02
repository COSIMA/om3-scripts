#!/usr/bin/bash -i
# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
# clean up cice_restarts.sh

if [ -f archive/output*/INPUT/iced.1900-01-01-10800.nc ]
then
rm archive/output*/INPUT/iced.1900-01-01-10800.nc
return 0
fi

latest_o=$(ls -drv archive/output*[0-9] | head -1)

#initial restart was copied from the previous run
ic_restart=$(ls -dv $latest_o/access-om3.cice.r.* | head -1)

if [ -f $latest_o/access-om3.cice.r.* ]
then
rm $latest_o/access-om3.cice.r.*
fi
