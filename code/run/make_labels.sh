#!/bin/bash
#SBATCH --partition=tarrq
#SBATCH --gres=gpu:0
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

cd ../utils/run/

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=1

# sublist=(1)
sublist=(1 2 3 4 5 6 7 8 999)

which_prf_grid=5

for subject in ${sublist[@]}
do
    python3 get_binary_prf_labels.py --subject $subject --debug $debug --which_prf_grid $which_prf_grid
    
    python3 get_highlevel_prf_labels.py --subject $subject --which_prf_grid $which_prf_grid
       
done

python3 count_labels --debug $debug --which_prf_grid $which_prf_grid

python3 concat_prf_labels --debug $debug --which_prf_grid $which_prf_grid
