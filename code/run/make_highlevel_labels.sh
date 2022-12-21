#!/bin/bash
#SBATCH --partition=tarrq
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

set -e 
source ~/myenv/bin/activate
# put the code directory on your python path
# (change this path)
PYTHONPATH=:/user_data/mmhender/image_stats_gabor/code/${PYTHONPATH}

echo $PYTHONPATH

cd /user_data/mmhender/image_stats_gabor/code/utils/run/

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=0

python3 make_highlevel_labels.py --debug $debug
