#!/usr/bin/bash -i
# Copyright 2024 ACCESS-NRI and contributors. See the top-level COPYRIGHT file for details.
# SPDX-License-Identifier: Apache-2.0
# 
# Concatenate sea-ice daily output from access-om3
# this was written assuming it would be used as a payu "userscript" at the "archive" stage, but alternatively a path to an "archive" directory can be provided
# Script inspired from https://github.com/COSIMA/1deg_jra55_ryf/blob/master/sync_data.sh#L87-L108
#
# This script uses "ncrcat". Load this through either 'module use /g/data/vk83/modules; module load payu' or 'module load nco'.

shopt -s extglob

Help()
{
   # Display Help
   echo "Concatenante daily history output from the (sea) ice model to a single file"
   echo
   echo "Syntax: scriptTemplate [-h|d DIRECTORY]"
   echo "options:"
   echo "h     Print this Help."
   echo "d     Process "name" directory rather than latest output in archive folder."
   echo
}

# Get the options
while getopts ":hd:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      d) # Enter a directory
         out_dir=$OPTARG
         if [ ! -d $out_dir ]; then 
            echo $out_dir Does not exist
            exit
         fi;;  
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

#If no directory option provided , then use latest
if [ -z $out_dir ]; then 
    #latest output dir only
    out_dir=$(ls -drv archive/output*[0-9] | head -1) 
fi

if ! command -v -- "ncrcat" > /dev/null 2>&1; then
    echo "ncrcat not available, trying module load nco"
    module load nco
fi

for f in $out_dir/access-om3.cice*.????-??-01.nc ; do
   output_f=${f/-01.nc/.nc} #remove day in date string

   if [ -f $output_f ]; then
      echo WARN: $output_f exists, skipping concatenation daily sea ice files
   #if the 1st and the 28th of that month exists, then assume its a whole month and concatenate
   elif [ -f $f ] && [ -f ${f/-01.nc/-28.nc} ] ; then 

      #concat daily files for this month
      echo LOG: concatenating daily sea ice files in $out_dir
      echo doing ncrcat -O -L 5 -4 ${f/-01.nc/-??.nc} $output_f
      ncrcat -O -L 5 -4 ${f/-01.nc/-??.nc} $output_f
      
      if [[ $? == 0 ]]; then 
         rm ${f/-01.nc/-??.nc} #delete individual dailys on success
      fi
   else
      echo "LOG: skipping concatenating daily sea ice files (incomplete month)"
   fi
done
