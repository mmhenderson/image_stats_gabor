import os, sys

from utils import nsd_utils
from utils import default_paths
from utils import coco_utils

nsd_root = default_paths.nsd_root
path_to_save = default_paths.stim_root

if __name__ == '__main__':
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--debug", type=int,default=0)
   
    args = parser.parse_args()
    
    
    
    nsd_utils.make_image_data_partitions(pct_holdout=0.10)
    
    nsd_utils.get_subject_specific_images(nsd_root, path_to_save, npix=240)

    coco_utils.get_coco_ids_indep(n_images=10000)

    coco_utils.prep_indep_coco_images(n_pix=240, debug=args.debug==1)
