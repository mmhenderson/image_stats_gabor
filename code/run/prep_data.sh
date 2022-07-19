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

python3 $code_dir/get_split_order.py

python3 resize_ims.py

python3 prep_indep_coco_ims.py --debug $debug
