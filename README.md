### Overview of repository contents: 
#### code
  - <b>analyze_features</b>: perform the image-statistic analyses: correlate Gabor features with semantic dimensions; decode semantic dimensions from Gabor features.
  - <b>analyze_fits</b>: estimate feature selectivity of voxels using encoding models fits; perform analyses of fit parameters.
  - <b>feature_extraction</b>: Compute the Gabor features (and AlexNet features) from input NSD images
  - <b>model_fitting</b>: Perform encoding model fitting. Main function to use is "fit_model.py" with various arguments.
  - <b>plotting</b>: Various utility functions for visualizing results.
  - <b>run</b>: Example shell scripts to execute model fitting. 
  - <b>utils</b>: Utility functions that are used by other functions. Note not all these functions are used by the code in this repository.
    - <b>utils/run</b>: convenience scripts to execute some of the functions utils folder. This folder includes the code needed to extract semantic category labels for each pRF.
  
 ### Notes
 - Where the subject ID string "999" is used, this indicates the set of 10,000 COCO images that were randomly selected for use in the image-statistics analyses (these were not viewed by any NSD participant).
 - If using any of the shell scripts in /code/run/, first ensure that the directory /code/run/sbatch_output/ exists. This folder will store the output of the shell script execution. 
 


