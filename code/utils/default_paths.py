
import os
import path_defs

nsd_root = path_defs.nsd_path
root = path_defs.root

# Where we are keeping the preprocessed NSD stimuli/labeling data
stim_root = os.path.join(root, 'nsd/stimuli/')    
stim_labels_root = os.path.join(root, 'nsd/labels/')    

# Where to save model fits
save_fits_path = os.path.join(root,'image_stats_gabor/model_fits/')

# Path where gabor model features will be saved
gabor_texture_feat_path = os.path.join(root, 'features/gabor_texture/')

# Path where AlexNet features will be saved
alexnet_feat_path = os.path.join(root, 'features/alexnet/')

# Where the raw beta weights are located
beta_root = os.path.join(nsd_root,'nsddata_betas','ppdata')
