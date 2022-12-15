#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --open-mode=append
#SBATCH --output=./sbatch_output/output-%A-%x-%u.out 
#SBATCH --time=8-00:00:00

source ~/myenv/bin/activate
# put the code directory on your python path
# (change this path)
PYTHONPATH=:/user_data/mmhender/image_stats_gabor/code/${PYTHONPATH}
PYTHONPATH=:/user_data/mmhender/toolboxes/RetinaFace-tf2/${PYTHONPATH}

echo $PYTHONPATH

cd /user_data/mmhender/image_stats_gabor/code/feature_extraction/

# to test the code, use debug=1
# to run for real, set debug=0 (False)
debug=0

# subject_list=(1)
subject_list=(1 2 3 4 5 6 7 8 999)

for subject in ${subject_list[@]}
do

    python3 label_faces.py --subject $subject --debug $debug

done