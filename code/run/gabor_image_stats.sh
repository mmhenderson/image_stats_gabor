#!/bin/bash
#SBATCH --partition=tarrq
#SBATCH --gres=gpu:0
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

source ~/myenv/bin/activate

# change this path
ROOT=/user_data/mmhender/

# put the code directory on your python path
PYTHONPATH=:${ROOT}image_stats_gabor/code/${PYTHONPATH}

# go to folder where script is located
cd ${ROOT}image_stats_gabor/code/analyze_features

which_prf_grid=5

subj=999
# subj=998
# 999 is a code for the independent set of 10000 images

feature_type=gabor_solo

# python3 get_feature_stats.py --subject $subj --debug $debug --feature_type $feature_type --which_prf_grid $which_prf_grid

python3 get_feature_sem_corrs.py --subject $subj --feature_type $feature_type --which_prf_grid $which_prf_grid