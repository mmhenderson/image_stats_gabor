#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --mem=100G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

source ~/myenv/bin/activate
# put the code directory on your python path
# (change this path)
PYTHONPATH=:/user_data/mmhender/TEST/image_stats_gabor/code/${PYTHONPATH}
echo $PYTHONPATH

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=1

python3 ../utils/run/prep_data.py --debug $debug
