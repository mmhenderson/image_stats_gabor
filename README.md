### Setup instructions:
<ol>
  <li>Clone the repository: 
    <ul>
    <li> git clone git@github.com:mmhenderson/image_stats_gabor
    </ul>
  <li>Edit "root" in path_defs.py to reflect the name of the folder into which you cloned this repository.
  <li>If using our pre-computed model fits: download the data from OSF
  <ul>
    <li> https://osf.io/dwehn/
    <li> After unzipping, you should have a folder "model_fits", which can be placed inside "image_stats_gabor".
    <li> You should also have a folder "rois", which should be placed at: /root/nsd/rois
    <li> Folder "feature_stats" and "feature_decoding" should be placed at: /root/features/gabor_texture/feature_stats and /root/features/gabor_texture/feature_decoding
    <li> Folder "labels" should be placed at: /root/nsd/labels/
  </ul>
  <li>If fitting from scratch: access the fMRI dataset (NSD) and images (COCO) here:
  <ul>
    <li> http://naturalscenesdataset.org/
    <li> https://cocodataset.org/
    <li> https://github.com/cocodataset/cocoapi
    <li> Update path_defs.py to reflect the paths where NSD and COCO are downloaded.
    <li> Next, prepare the image data & extract features (using files in /code/run/):
      <ul>
        <li> prep_data.sh
        <li> prep_data_indep_big.sh
        <li> label_faces.sh
        <li> make_labels_all.sh
        <li> subsample_trials.sh
        <li> extract_gabor_features.sh
        <li> extract_alexnet_features.sh
        <li> ^ Before executing above scripts, modify the first few lines to reflect paths on your local filesystem. You may need to change other parameters: by default, we have set "debug=1", so the code runs a shortened test version. To run it for real, set debug=0. If you'd like to run all subjects, you should also change the "subjects" variable to a list over all subjects (1-8). Include "998" in the subjects list to extract features for our independent image set.
      </ul>
    <li> Code to perform image statistics analyses:
      <ul>
        <li> gabor_image_stats.sh
        <li> gabor_categ_decoding.sh
      </ul>
    <li> Code to fit models:
       <ul>
        <li> fit_alexnet.sh (fit AlexNet encoding model, including pRFs)
        <li> fit_gabor.sh (fit Gabor model using AlexNet pRFs)
        <li> fit_gabor_fromscratch.sh (fit Gabor model from scratch, including pRFs)
        <li> fit_cocoall.sh (fit COCO-all semantic category model; save its residuals)
        <li> fit_gabor_fromresid.sh (fit Gabor model using residuals of COCO-all model)
        <li> fit_gabor_withincateg.sh (fit Gabor model using images of one category at a time).
      </ul>
    </li> 
   </ul>
  <li>Use the jupyter notebooks in "plotting_notebooks" to plot the results of model fitting, and reproduce all our figures.
 </ol>
 
  
### Other notes
 - Where the subject ID string "998" is used, this indicates the set of 50,000 COCO images that were randomly selected for use in the image-statistics analyses (these were not viewed by any NSD participant).
 - If using a workload manager (slurm) to execute the shell scripts in /code/run/, first ensure that the directory /code/run/sbatch_output/ exists. This folder will store the output of the shell script execution. 
 

Please contact mmhender@cmu.edu with any questions or concerns.
