#!/bin/bash

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# define directory structure (edit here)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

export DIR_HECTOR=$HOME/Documents/CarbonPlan/code/hector
export DIR_PROJECT=$HOME/Documents/CarbonPlan/normalizing-cdr-accounting
export DIR_OUTPUT=$DIR_PROJECT/data/hector-output
export HECTOR_INPUT=$DIR_PROJECT/data/hector-forcing/test-short-preindustrial/short_test.ini

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# get information about simulation
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Get run name (for saving output)
result=$(ls -l | grep run_name $HECTOR_INPUT)
IFS='=' # Set this as the delimiter
read -a strarr <<< "$result" #Read the split words into an array
run_name=${strarr[1]}

# Get date and time (for saving output)
# NOTE this is temporary while figuring out workflow - ultimately date and time should
# probably not be in folder names
today="$(date +'%Y%b%d_%H%M')"

# Make folder for output
DIR_OUTPUT_SIM=$DIR_OUTPUT/output_${run_name}_${today}
mkdir -p $DIR_OUTPUT_SIM

fname_log=$DIR_OUTPUT_SIM/log_${run_name}_${today}.txt
echo "Output to be saved in ${DIR_OUTPUT_SIM}">> $fname_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# make hector
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
cd $DIR_HECTOR

echo "run_name = ${run_name}" >> $fname_log
echo "---------------- Making hector-------------" >> $fname_log 
make hector >> $fname_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# run hector
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
echo "---------------- Running hector-------------" >> $fname_log
./src/hector $HECTOR_INPUT >> $fname_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# move files to target directory for output
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Get info about files to copy
DIR_OUTPUT_DEFAULT=$DIR_HECTOR/output
fname_output_tracking=${DIR_OUTPUT_DEFAULT}/tracking_${run_name}.csv
fname_output_outputstream=${DIR_OUTPUT_DEFAULT}/outputstream_${run_name}.csv

# Copy the files
# NOTE eventually move them instead of copying them?
cd $DIR_OUTPUT_SIM
cp $fname_output_tracking .
cp $fname_output_outputstream .
echo "Output saved in ${DIR_OUTPUT_SIM}">> $fname_log
