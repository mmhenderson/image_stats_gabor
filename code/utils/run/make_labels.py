import os, sys, argparse
import numpy as np

from utils import label_utils
from utils import default_paths

nsd_root = default_paths.nsd_root
path_to_save = default_paths.stim_root
print('nsd_root: %s'%nsd_root)
print('path_to_save: %s'%path_to_save)

if not os.path.exists(path_to_save):
    os.makedirs(path_to_save)
    
if __name__ == '__main__':
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--debug", type=int,default=0,
                    help="want to run a fast test version of this script to debug? 1 for yes, 0 for no")
   
   
    args = parser.parse_args()

    print('debug=%d'%args.debug)
    
    which_prf_grid=5
    
    for subject in np.arange(1,9):

        # doing these labels separately for coco labels (objects) and coco-stuff
        label_utils.write_binary_labels_csv_within_prf(subject=subject, min_pix=10, debug=args.debug==1, stuff=False, which_prf_grid=which_prf_grid)
        label_utils.write_binary_labels_csv_within_prf(subject=subject, min_pix=10, debug=args.debug==1, stuff=True, which_prf_grid=which_prf_grid)

        # higher-level semantic dimensions
        label_utils.write_indoor_outdoor_csv(subject=subject)
        label_utils.write_natural_humanmade_csv(subject=subject, which_prf_grid=which_prf_grid)
        label_utils.write_realworldsize_csv(subject=subject, which_prf_grid=which_prf_grid)
    
    # counting occurences of each label
    label_utils.count_labels_each_prf(which_prf_grid=which_prf_grid, debug=args.debug==1)
    label_utils.get_top_two_subcateg(which_prf_grid=which_prf_grid)

    for subject in np.arange(1,9):

        label_utils.concat_labels_each_prf(subject=subject, \
                                      which_prf_grid=which_prf_grid, verbose=True)