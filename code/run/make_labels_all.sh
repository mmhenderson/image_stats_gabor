#!/bin/bash
#SBATCH --partition=tarrq
#SBATCH --gres=gpu:0
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

source ~/myenv/bin/activate
# put the code directory on your python path
# (change this path)
# PYTHONPATH=:/user_data/mmhender/TEST/image_stats_gabor/code/${PYTHONPATH}
PYTHONPATH=:/user_data/mmhender/modfit/code/${PYTHONPATH}

echo $PYTHONPATH

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=0

cd /user_data/mmhender/modfit/code/utils/run/

python3 make_labels.py --debug $debug

python3 make_labels_indep_big.py --debug $debug

# need to run label_faces before this
python3 make_highlevel_labels.py --debug $debug

