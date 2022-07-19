#!/bin/bash
#SBATCH --partition=tarrq
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

debug=1
up_to_sess=1
which_prf_grid=5

for subject in ${subjects[@]}
do

    python3 semantic_discrim_raw.py --subject $subject --up_to_sess $up_to_sess --debug $debug --which_prf_grid $which_prf_grid
    
done