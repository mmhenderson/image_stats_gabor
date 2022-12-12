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

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=0

which_prf_grid=5

subjects=(1 2 3 4 5 6 7 8)
# subjects=(8)

feature_type=gabor_solo

trial_subset_list=(balance_indoor_outdoor outdoor_only indoor_only balance_animacy animate_only inanimate_only balance_real_world_size_binary large_only small_only)
# trial_subset_list=(balance_indoor_outdoor)

for subject in ${subjects[@]}
do

    for trial_subset in ${trial_subset_list[@]}
    do

        python3 get_feature_stats.py --subject $subject --debug $debug --feature_type $feature_type --which_prf_grid $which_prf_grid --trial_subset $trial_subset

    done
done