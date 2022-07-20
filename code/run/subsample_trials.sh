#!/bin/bash
#SBATCH --partition=cpu
#SBATCH --gres=gpu:0
#SBATCH --mem=16G
#SBATCH --exclude=mind-1-13
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

echo $SLURM_JOBID
echo $SLURM_NODELIST

source ~/myenv/bin/activate

# change this path
ROOT=/user_data/mmhender/TEST/

# put the code directory on your python path
PYTHONPATH=:${ROOT}image_stats_gabor/code/${PYTHONPATH}

# go to folder where script is located
cd ${ROOT}image_stats_gabor/code/model_fitting

# subjects=(1 2 3 4 5 6 7 8)
subject_list=(1)

debug=1

n_samp_iters=10
separate_categ=1

for subject in ${subject_list[@]}
do
    python3 subsample_trials.py --subject $subject --debug $debug --n_samp_iters $n_samp_iters --separate_categ $separate_categ
    
done