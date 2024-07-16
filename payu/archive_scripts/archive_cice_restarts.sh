#!/usr/bin/bash -i
# clean up cice_restarts.sh

latest_o=$(ls -drv archive/output*[0-9] | head -1)

if [ -f $latest_o/access-om3.cice.r.* ]
then
rm $latest_o/access-om3.cice.r.*
fi

if [ -f archive/output*/input/iced.1900-01-01-10800.nc ] 
then
rm archive/output*/input/iced.1900-01-01-10800.nc
fi
