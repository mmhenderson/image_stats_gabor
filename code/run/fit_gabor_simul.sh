#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --exclude=mind-1-13
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

echo $SLURM_JOBID
echo $SLURM_NODELIST

source ~/myenv/bin/activate

# change this path
ROOT=/user_data/mmhender/

# put the code directory on your python path
PYTHONPATH=:${ROOT}image_stats_gabor/code/${PYTHONPATH}

# go to folder where script is located
cd ${ROOT}image_stats_gabor/code/model_fitting

# subjects=(1 2 3 4 5 6 7 8)
subjects=(1)


# debug=1
# up_to_sess=1

debug=0
up_to_sess=40

# use the pre-computed pRFs here, for main analysis
use_precomputed_prfs=1
which_prf_grid=5

do_val=1
from_scratch=1
do_tuning=1

fitting_type=gabor_solo

n_ori_gabor=12
n_sf_gabor=8

use_simulated_data=1
simul_model_name='gabor'
simul_noise_level=0.10

trial_subset_list=(both_animate-inanimate animate inanimate both_small-large small large both_indoor-outdoor indoor outdoor)

for subject in ${subjects[@]}
do

    for trial_subset in ${trial_subset_list[@]}
    do

        python3 fit_model.py --subject $subject --debug $debug --up_to_sess $up_to_sess --use_precomputed_prfs $use_precomputed_prfs --which_prf_grid $which_prf_grid --from_scratch $from_scratch --do_val $do_val --do_tuning $do_tuning --fitting_type $fitting_type --n_ori_gabor $n_ori_gabor --n_sf_gabor $n_sf_gabor --use_simulated_data $use_simulated_data --simul_model_name $simul_model_name --simul_noise_level $simul_noise_level --trial_subset $trial_subset
        
    done
    
done