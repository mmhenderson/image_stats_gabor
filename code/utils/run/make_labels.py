import os, sys, argparse
import numpy as np

from utils import label_utils
from utils import default_paths

nsd_root = default_paths.nsd_root
labels_path = default_paths.stim_labels_root

print('nsd_root: %s'%nsd_root)
print('labels_path: %s'%labels_path)
 
if __name__ == '__main__':
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--debug", type=int,default=0,
                    help="want to run a fast test version of this script to debug? 1 for yes, 0 for no")
   
   
    args = parser.parse_args()
    debug=args.debug==1
    
    print('debug=%d'%debug)
    
    which_prf_grid=5
    
    if debug:
        subjects = [1, 999]
    else:
        subjects = list(np.arange(1,9))+[999]
        
    for subject in subjects:

        label_utils.write_binary_labels_csv(subject=subject, stuff=False)
        label_utils.write_binary_labels_csv(subject=subject, stuff=True)
        
        # doing these labels separately for coco labels (objects) and coco-stuff
        label_utils.write_binary_labels_csv_within_prf(subject=subject, min_pix=10, debug=debug, stuff=False, which_prf_grid=which_prf_grid)
        label_utils.write_binary_labels_csv_within_prf(subject=subject, min_pix=10, debug=debug, stuff=True, which_prf_grid=which_prf_grid)

        # higher-level semantic dimensions
        label_utils.write_indoor_outdoor_csv(subject=subject)
        label_utils.write_natural_humanmade_csv(subject=subject, which_prf_grid=which_prf_grid, debug=debug)
        label_utils.write_realworldsize_csv(subject=subject, which_prf_grid=which_prf_grid, debug=debug)
    
    # counting occurences of each label
    label_utils.count_labels_each_prf(which_prf_grid=which_prf_grid, debug=debug)
    label_utils.get_top_two_subcateg(which_prf_grid=which_prf_grid)

    for subject in subjects:

        label_utils.concat_labels_each_prf(subject=subject, \
                                      which_prf_grid=which_prf_grid, verbose=True, debug=debug)
        label_utils.concat_labels_fullimage(subject=subject, verbose=True)
        
    label_utils.count_highlevel_labels(which_prf_grid=which_prf_grid, axes_to_do=[0,2,3], \
                           debug=debug)