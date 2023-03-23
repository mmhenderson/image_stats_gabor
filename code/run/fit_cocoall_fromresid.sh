#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --exclude=mind-1-13,mind-1-32,mind-1-34
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

subjects=(1 2 3 4 5 6 7 8)
# subjects=(1)


# debug=1
# up_to_sess=1

debug=0
up_to_sess=40

use_precomputed_prfs=1
which_prf_grid=5

do_val=1
from_scratch=1
do_tuning=0

fitting_type=semantic
semantic_feature_set=all_coco

use_model_residuals=1
residuals_model_name=gabor_solo_ridge_12ori_8sf

for subject in ${subjects[@]}
do

    python3 fit_model.py --subject $subject --debug $debug --up_to_sess $up_to_sess --use_precomputed_prfs $use_precomputed_prfs --which_prf_grid $which_prf_grid --from_scratch $from_scratch --do_val $do_val --do_tuning $do_tuning --fitting_type $fitting_type --semantic_feature_set $semantic_feature_set --use_model_residuals $use_model_residuals --residuals_model_name $residuals_model_name
    
done