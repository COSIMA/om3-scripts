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

# Assume no leap year by default
declare -A DAYS_IN_MONTH=(
    [01]=31 [02]=28 [03]=31 [04]=30 [05]=31 [06]=30
    [07]=31 [08]=31 [09]=30 [10]=31 [11]=30 [12]=31
)

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
   # extract the year and month from existing files
   year_month=$(echo "$f" | sed -E "s/.*\.([0-9]{4}-[0-9]{2})-[0-9]{2}\.nc/\1/")
   year=$(echo "$year_month" | cut -d- -f1)
   month=$(echo "$year_month" | cut -d- -f2)

   # get expected end day, allowing 29 if present on Feburary
   # if the month is Feb and a `-29.nc` file exists, allow 29 days
   # we cannot use the year to determine leap years because RYF configurations
   # don't follow a standard calendar. 
   end_day=${DAYS_IN_MONTH[$month]}
   if [[ $month == "02" ]] && [[ -f ${f/-01.nc/-29.nc} ]]; then
      end_day=29
   fi

   # expected last day file
   end_day_file=${f/-01.nc/-${end_day}.nc}

   output_f=${f/-01.nc/.nc} #remove day in date string

   if [ -f $output_f ]; then
      echo WARN: $output_f exists, skipping concatenation daily sea ice files
   elif [ -f $f ] && [ -f $end_day_file ] ; then
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
