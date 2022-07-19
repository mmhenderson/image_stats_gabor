### Setup instructions:
<ol>
  <li>Clone the repository: 
    <ul>
    <li> git clone git@github.com:mmhenderson/image_stats_gabor
    </ul>
  <li>Edit "root" in path_defs.py to reflect the name of the folder into which you cloned this repository.
  <li>Access the fMRI dataset (NSD) and images (COCO) here:
  <ul>
    <li> http://naturalscenesdataset.org/
    <li> https://cocodataset.org/
    <li> https://github.com/cocodataset/cocoapi
    <li> Once you download these, update the paths in path_defs.py accordingly.
   </ul>
  <li>If using our pre-computed features or model fits (from XXX OSF repo XXX), these should be placed in a folder on the same level as this repository (i.e., also inside "root").
  <li> Add the code to your python path:
    <ul>
    <li> PYTHONPATH=:/your_root/image_stats_gabor/code/$PYTHONPATH
    </ul>
  <li> Navigate to script directory:
    <ul>
      <li> cd code/run
    </ul>
  <li> Prepare the image data/extract features:
    <ul>
      <li> prep_data.sh
      <li> make_labels.sh
      <li> extract_gabor_features.sh
      <li> extract_alexnet_features.sh
      <li> ^ Before executing above scripts, modify the first few lines to reflect paths on your local filesystem. You can also change other parameters: by default, we have set "debug=1", so the code runs a shortened test version. To run it for real, set debug=0. If you'd like to run all subjects, you should also change the "subjects" variable to a list over all subjects (1-8).
    </ul>
  <li> Image statistics analyses:
    <ul>
      <li> gabor_image_stats.sh
      <li> gabor_decoding.sh
    </ul>
  <li> Fit models:
    <ul>
      <li> fit_alexnet.sh (fit AlexNet encoding model, including pRFs)
      <li> fit_gabor.sh (fit Gabor model using AlexNet pRFs)
      <li> fit_gabor_fromscratch.sh (fit Gabor model from scratch, including pRFs)
      <li> fit_cocoall.sh (fit COCO-all semantic category model; save its residuals)
      <li> fit_gabor_fromresid.sh (fit Gabor model using residuals of COCO-all model)
      <li> fit_gabor_withincateg.sh (fit Gabor model using images of one category at a time).
    </ul>
  <li>Visualize results using jupyter notebooks (see below for details).
 </ol>
 
 
### Overview of repository contents:
- <b>code</b>
  - <b>analyze_features</b>: Perform the image-statistic analyses: correlate Gabor features with semantic dimensions; decode semantic dimensions from Gabor features.
  - <b>analyze_fits</b>: Estimate feature selectivity of voxels using encoding models fits; perform analyses of fit parameters.
  - <b>feature_extraction</b>: Compute the Gabor features and AlexNet features from input NSD images.
  - <b>model_fitting</b>: Perform encoding model fitting. Main function to use is "fit_model.py" with various arguments to control the type of fitting (see argparse.py for options).
  - <b>plotting</b>: Various utility functions for visualizing results.
  - <b>run</b>: Example shell scripts to execute model fitting. 
  - <b>utils</b>: Utility functions that are used by other functions. Note not all these functions are used here.
    - <b>utils/run</b>: Convenience scripts to execute some of the functions utils folder. This folder includes the code needed to extract semantic category labels for each pRF.
- <b>make_roi_tables</b>
    - Create tables of the number of voxels in each ROI (our Supplementary Tables 1-4).
- <b>plot_feature_selectivity</b>
    - Plot feature sensitivity profiles and distribution of preferred features.
    - Main analyses (Figure 3, and Supplementary Figures 1, 2, 6) are plotted in plot_gabor_tuning.ipynb
    - Fits to category model residuals (Figure 5) are plotted in plot_gabor_tuning_semresiduals.ipynb
    - Fits within semantic category (Figure 6) are plotted in plot_gabor_tuning_trialsubsets.ipynb
    - Counting the number of peaks in sensitivity profiles (Supplementary Figure 3) is in plot_gabor_tuning_multipeaks.ipynb
    - Results for a smaller version of the Gabor model (not included in our paper) are plotted in plot_gabor_tuning_4x4.ipynb
- <b>plot_image_stats</b>
    - Visualize results of the image-statistics analyses (Figure 2).
- <b>plot_prfs</b>
    - Make plots of pRF parameters and pRF coverage of the visual field.
    - For our main analyses (Figure 4, Supplementary Figure 4), use plot_prf_params_alexnet.ipynb and plot_prf_coverage_alexnet.ipynb
    - For the supplementary analysis where we fitted pRFs using Gabor features (Supplementary Figure 5), use plot_prf_params_gabor.ipynb and plot_prf_coverage_gabor.ipynb
- <b>plot_summary</b>
     - Make plots of overall model performance and overall semantic selectivity of voxels (Figure 1)
 
### Other notes
 - Where the subject ID string "999" is used, this indicates the set of 10,000 COCO images that were randomly selected for use in the image-statistics analyses (these were not viewed by any NSD participant).
 - Some of the code includes references to other feature spaces (CLIP, sketch tokens). We did not include those feature sets in this paper, but you can see more code related to these other feature sets in our other repository at: github.com/mmhenderson/modfit
 - If using any of the shell scripts in /code/run/, first ensure that the directory /code/run/sbatch_output/ exists. This folder will store the output of the shell script execution. 
 


