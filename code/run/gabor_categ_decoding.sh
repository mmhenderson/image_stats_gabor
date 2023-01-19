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

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=0

subj=998
# subj=999
# 999 is a code for the independent set of 10000 images

n_samp_iters=2
balance_categ_for_decoding_matchprfs=1
balance_for_decoding=0
balance_for_decoding_matchprfs=0

cd ${ROOT}image_stats_gabor/code/model_fitting

python3 subsample_trials.py --subject $subj --debug $debug --n_samp_iters $n_samp_iters --balance_for_decoding $balance_for_decoding --balance_for_decoding_matchprfs $balance_for_decoding_matchprfs --balance_categ_for_decoding_matchprfs $balance_categ_for_decoding_matchprfs

feature_type=gabor_solo
which_prf_grid=5

cd ${ROOT}image_stats_gabor/code/analyze_features

match_prf_trialcounts=1
categ_vs_none=1

python3 decode_categ_from_features.py --subject $subj --debug $debug --feature_type $feature_type --which_prf_grid $which_prf_grid --match_prf_trialcounts $match_prf_trialcounts --categ_vs_none $categ_vs_none
 