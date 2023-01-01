# Set "root" to your top-level directory
root = '/user_data/mmhender/'

# Inside "root" should be the subfolders:
#     "nsd" which includes our pre-processed images from NSD
#     "image_stats_gabor" (main project folder with all our code)
#     "features" (precomputed features extracted for each pRF)
# If you're just trying to load our models that have already been fit (not fitting
# from scratch), then you only need the "image_stats_gabor" folder

project_name = 'image_stats_gabor'

# Set path to the full NSD data repository (this is where the beta weights are stored)
# http://naturalscenesdataset.org/
# This is only needed if you want to fit from scratch
nsd_path = '/lab_data/tarrlab/common/datasets/NSD'   
# nsd_path = ''

# Path to the COCO API toolbox
# https://github.com/cocodataset/cocoapi
coco_api_path = '/user_data/mmhender/toolboxes/coco_annot'
# coco_api_path = ''

# Path to where the raw COCO images are stored
# https://cocodataset.org/
coco_ims_path = '/lab_data/tarrlab/common/datasets/COCO'
# coco_ims_path = ''

retinaface_path = '/user_data/mmhender/toolboxes/RetinaFace-tf2/'