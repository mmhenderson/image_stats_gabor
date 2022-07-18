### Setup instructions:
<ol>
  <li>Clone the repository: 
  <ul>
    <li> git clone https://github/com/mmhender/image_stats_gabor
  </ul>
  <li>Edit "root" in path_defs.py to reflect the name of the folder into which you cloned this repository.
  <li>If using our pre-computed features or model fits (from XXX OSF repo XXX), these should be placed in a folder on the same level as this repository (i.e., also inside "root").
 </ol>
 
 
### Overview of repository contents:
- code
  - <b>analyze_features</b>: Perform the image-statistic analyses: correlate Gabor features with semantic dimensions; decode semantic dimensions from Gabor features.
  - <b>analyze_fits</b>: Estimate feature selectivity of voxels using encoding models fits; perform analyses of fit parameters.
  - <b>feature_extraction</b>: Compute the Gabor features and AlexNet features from input NSD images.
  - <b>model_fitting</b>: Perform encoding model fitting. Main function to use is "fit_model.py" with various arguments to control the type of fitting (see argparse.py for options).
  - <b>plotting</b>: Various utility functions for visualizing results.
  - <b>run</b>: Example shell scripts to execute model fitting. 
  - <b>utils</b>: Utility functions that are used by other functions. Note not all these functions are used here.
    - <b>utils/run</b>: Convenience scripts to execute some of the functions utils folder. This folder includes the code needed to extract semantic category labels for each pRF.
- <b>make_roi_tables</b>: Create tables of the number of voxels in each ROI (our Supplementary Tables 1-4).
- <b>plot_feature_selectivity</b>: Plot feature sensitivity profiles and distribution of preferred features.
    - Main analyses (Figure 3, and Supplementary Figures 1, 2, 6) are plotted in plot_gabor_tuning.ipynb
    - Fits to category model residuals (Figure 5) are plotted in plot_gabor_tuning_semresiduals.ipynb
    - Fits within semantic category (Figure 6) are plotted in plot_gabor_tuning_trialsubsets.ipynb
    - Counting the number of peaks in sensitivity profiles (Supplementary Figure 3) is in plot_gabor_tuning_multipeaks.ipynb
    - Results for a smaller version of the Gabor model (not included in our paper) are plotted in plot_gabor_tuning_4x4.ipynb
- <b>plot_image_stats</b>: Visualize results of the image-statistics analyses (Figure 2).
- <b>plot_prfs</b>: Make plots of pRF parameters and pRF coverage of the visual field.
    - For our main analyses (Figure 4, Supplementary Figure 4), use plot_prf_params_alexnet.ipynb and plot_prf_coverage_alexnet.ipynb
    - For the supplementary analysis where we fitted pRFs using Gabor features (Supplementary Figure 5), use plot_prf_params_gabor.ipynb and plot_prf_coverage_gabor.ipynb
- <b>plot_summary</b>: Make plots of overall model performance and overall semantic selectivity of voxels (Figure 1)
 
### Other notes
 - Where the subject ID string "999" is used, this indicates the set of 10,000 COCO images that were randomly selected for use in the image-statistics analyses (these were not viewed by any NSD participant).
 - Some of the code includes references to other feature spaces (CLIP, sketch tokens). We did not include those feature sets in this paper, but you can see more code related to these other feature sets in our other repository at: github.com/mmhenderson/modfit
 - If using any of the shell scripts in /code/run/, first ensure that the directory /code/run/sbatch_output/ exists. This folder will store the output of the shell script execution. 
 


