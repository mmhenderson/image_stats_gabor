
"""
These are all semi-general functions that are run before model fitting (file name to save, make feature extractors etc.)
"""

import torch
import time
import os, sys
import numpy as np
import pandas as pd
from datetime import datetime

# import custom modules
from feature_extraction import fwrf_features, semantic_features, merge_features
from utils import prf_utils, default_paths, nsd_utils, label_utils
from model_fitting import saved_fit_paths

def init_cuda():
    
    # Set up CUDA stuff
    
    print ('#device:', torch.cuda.device_count())
    print ('device#:', torch.cuda.current_device())
    print ('device name:', torch.cuda.get_device_name(torch.cuda.current_device()))

    torch.manual_seed(time.time())
    device = torch.device("cuda:0") #cuda
    torch.backends.cudnn.enabled=True

    print ('\ntorch:', torch.__version__)
    print ('cuda: ', torch.version.cuda)
    print ('cudnn:', torch.backends.cudnn.version())
    print ('dtype:', torch.get_default_dtype())

    return device

def get_full_save_name(args):

    input_fitting_types = [args.fitting_type, args.fitting_type2, args.fitting_type3]
    input_fitting_types = [ft for ft in input_fitting_types if ft!='']
    fitting_types = [] # this is a list of all the feature types to include, used to create modules.
    model_name = '' # model_name is a string used to name the folder we will save to
    for fi, ft in enumerate(input_fitting_types):
        print(ft)
        if ft=='full_midlevel':
            
            fitting_types += ['gabor_solo', 'pyramid_texture','sketch_tokens']
            model_name += 'full_midlevel'
            
        elif ft=='concat_midlevel':
           
            fitting_types += ['color_noavg','gabor_solo_noavg', 'pyramid_texture','sketch_tokens']
            model_name += 'concat_midlevel'
            assert(args.prfs_model_name=='texture')
            
        elif ft=='semantic':
            if args.semantic_feature_set=='all_coco':
                fitting_types += ['semantic_coco_things_supcateg','semantic_coco_things_categ',\
                             'semantic_coco_stuff_supcateg','semantic_coco_stuff_categ']
                model_name += 'all_coco'
            elif args.semantic_feature_set=='all_coco_stuff':
                fitting_types += ['semantic_coco_stuff_supcateg','semantic_coco_stuff_categ']
                model_name += 'all_coco_stuff'
            elif args.semantic_feature_set=='all_coco_things':
                fitting_types += ['semantic_coco_things_supcateg','semantic_coco_things_categ']
                model_name += 'all_coco_things'
            elif args.semantic_feature_set=='all_coco_categ':
                fitting_types += ['semantic_coco_things_categ','semantic_coco_stuff_categ']
                model_name += 'all_coco_categ'
            elif args.semantic_feature_set=='all_coco_categ_pca':
                fitting_types += ['semantic_coco_things_categ_pca','semantic_coco_stuff_categ_pca']
                model_name += 'all_coco_categ_pca'
            elif args.semantic_feature_set=='highlevel_concat':
                fitting_types += ['semantic_indoor_outdoor', 'semantic_animacy', 'semantic_real_world_size']
                model_name += 'semantic_highlevel_concat'
            else:
                fitting_types += ['semantic_%s'%args.semantic_feature_set]
                model_name += 'semantic_%s'%args.semantic_feature_set
                
        elif 'texture_pyramid' in ft:
            fitting_types += [ft]
            model_name += 'texture_pyramid'
            if args.ridge==True:   
                model_name += '_ridge'
            else:
                model_name += '_OLS'
            model_name += '_%dori_%dsf'%(args.n_ori_pyr, args.n_sf_pyr)  
            if args.pyr_pca_type is not None:
                model_name += '_%s'%args.pyr_pca_type
              
            if not args.group_all_hl_feats:
                model_name += '_allsubsets'
           
                
        elif 'gabor_solo' in ft:     
            fitting_types += [ft]
            model_name += 'gabor_solo'
            if args.ridge==True:   
                model_name += '_ridge'
            else:
                model_name += '_OLS'
            model_name+='_%dori_%dsf'%(args.n_ori_gabor, args.n_sf_gabor)
            if 'noavg' in ft:
                model_name += '_noavg'
            elif args.use_pca_gabor_feats:
                model_name += '_pca'           
            
        elif 'sketch_tokens' in ft:      
            fitting_types += [ft]
            if args.use_pca_st_feats==True:       
                model_name += 'sketch_tokens_pca'
            elif args.use_residual_st_feats==True:
                model_name += 'sketch_tokens_residuals'
            else:        
                model_name += 'sketch_tokens'
            if args.use_grayscale_st_feats:
                model_name += '_gray'
            if 'noavg' in ft:
                model_name += '_noavg'
                if args.st_use_avgpool:
                    model_name += '_avgpool'
                else:
                    model_name += '_maxpool'
                model_name += '_poolsize%d'%args.st_pooling_size
        
        elif 'gist' in ft:
            
            fitting_types += [ft]
            model_name += 'gist_%dori'%(args.n_ori_gist)
            if args.n_blocks_gist!=4:
                model_name += '_%dblocks'%args.n_blocks_gist
                
        elif 'color' in ft:
            fitting_types += [ft]
            model_name += 'color_cielab_sat'
            if 'noavg' in ft:
                model_name += '_noavg'
          
        elif 'alexnet' in ft:
            fitting_types += [ft]
            if 'ReLU' in args.alexnet_layer_name:
                name = args.alexnet_layer_name.split('_')[0]
            else:
                name = args.alexnet_layer_name
            if args.alexnet_blurface:
                model_name += 'alexnet_blurface_%s'%name               
            else:
                model_name += 'alexnet_%s'%name
            if args.use_pca_alexnet_feats:
                model_name += '_pca'
            if 'noavg' in ft:
                model_name += '_noavg'
                
        elif 'clip' in ft:
            fitting_types += [ft]
            if args.resnet_layer_name=='best_layer' and args.n_resnet_blocks_include<16:
                layer_name = 'best_layer_of%d'%args.n_resnet_blocks_include
            else:
                layer_name = args.resnet_layer_name
            model_name += 'clip_%s_%s'%(args.resnet_model_architecture, layer_name)
            if args.use_pca_resnet_feats:
                model_name += '_pca'
            if 'noavg' in ft:
                model_name += '_noavg'
                
        elif 'resnet' in ft:
            fitting_types += [ft]
            if args.resnet_layer_name=='best_layer' and args.n_resnet_blocks_include<16:
                layer_name = 'best_layer_of%d'%args.n_resnet_blocks_include
            else:
                layer_name = args.resnet_layer_name
            if args.resnet_blurface:
                model_name += 'resnet_blurface_%s_%s'%(args.resnet_model_architecture, layer_name)
            elif 'startingblurry' in ft:
                model_name += 'resnet_%s_%s'%(args.resnet_training_type, layer_name)
            else:
                model_name += 'resnet_%s_%s'%(args.resnet_model_architecture, layer_name)
            assert (args.use_pca_resnet_feats==True)
            if 'noavg' in ft:
                model_name += '_noavg'
                
        else:
            raise ValueError('fitting type "%s" not recognized'%ft)
        
        if fi<len(input_fitting_types)-1:
            model_name+='_plus_'
            
    if args.trial_subset!='all':
        model_name += '_%s'%args.trial_subset
    if args.use_model_residuals:
        model_name += '_from_residuals'
        
    if args.use_simulated_data:
        model_name += '_simulated_%s_addnoise_%.2f'%(args.simul_model_name, args.simul_noise_level)
        
    if not args.use_precomputed_prfs:
        if 'alexnet' not in model_name and args.which_prf_grid!=0:
            model_name += '_fit_pRFs'
    elif len(args.prfs_model_name)>0 and 'concat_midlevel' not in model_name:
        model_name += '_use_%s_pRFs'%args.prfs_model_name
        
    if args.which_prf_grid!=5:
        model_name += '_pRFgrid_%d'%args.which_prf_grid
    
    if args.prf_fixed_sigma is not None:
        model_name += '_fixsigma%.3f'%args.prf_fixed_sigma
            
    if args.shuffle_data:
        model_name += '_permutation_test'
    if args.bootstrap_data:
        if args.boot_val_only:
            model_name += '_bootstrap_test_val'        
        else:
            model_name += '_bootstrap_test'
        
    print(fitting_types)
    print(model_name)
    
    return model_name, fitting_types


def get_save_path(model_name, args):
    
    # choose where to save results of fitting - always making a new file w current timestamp.
    # add these suffixes to the file name if it's one of the control analyses
    if args.shuffle_images_once==True:
        model_name = model_name + '_SHUFFLEIMAGES'
    if args.random_images==True:
        model_name = model_name + '_RANDOMIMAGES'
    if args.random_voxel_data==True:
        model_name = model_name + '_RANDOMVOXELDATA'
    
    save_fits_path = default_paths.save_fits_path
    if args.volume_space:
        subject_dir = os.path.join(save_fits_path, 'S%02d'%args.subject)
    else:
        subject_dir = os.path.join(save_fits_path,'S%02d_surface'%args.subject)
    
    if args.from_scratch:
        timestamp = time.strftime('%b-%d-%Y_%H%M_%S', time.localtime())
        make_new_folder = True
    elif (args.date_str=='') or (args.date_str=='0'):
        # load most recent file
        files_in_dir = os.listdir(os.path.join(subject_dir, model_name))   
        if not args.debug:
            my_dates = [f for f in files_in_dir if 'ipynb' not in f and 'DEBUG' not in f]
        else:
            my_dates = [f for f in files_in_dir if 'ipynb' not in f and 'DEBUG' in f]
            my_dates = [date.split('_DEBUG')[0] for date in my_dates]
        try:
            my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M_%S"))
        except:
            my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M"))
        most_recent_date = my_dates[-1]
        timestamp = most_recent_date
        make_new_folder = False
    else:
        # if you specified an existing timestamp, then won't try to make new folder, need to find existing one.
        timestamp = args.date_str
        make_new_folder = False
        
    print ("Time Stamp: %s" % timestamp)  
    
    if args.debug==True:
        output_dir = os.path.join(subject_dir,model_name,'%s_DEBUG/'%timestamp)
    else:
        output_dir = os.path.join(subject_dir,model_name,'%s'%timestamp)
    if not os.path.exists(output_dir): 
        if make_new_folder:
            os.makedirs(output_dir)
        else:
            raise ValueError('the path at %s does not exist yet!!'%output_dir)
        
    fn2save = os.path.join(output_dir,'all_fit_params.npy')
    print('\nWill save final output file to %s\n'%output_dir)
    
    return output_dir, fn2save
 
def get_lambdas(fitting_types, zscore_features=True, ridge=True):
    
    if ridge==False:
        lambdas = np.array([0.0,0.0])        
    else:
        if zscore_features==True:
            lambdas = np.logspace(np.log(0.01),np.log(10**5+0.01),9, dtype=np.float32, base=np.e) - 0.01
        else:
            # range of feature values are different if choosing not to z-score. the performance of these lambdas
            # will vary depending on actual feature value ranges, be sure to check the results carefully
            lambdas = np.logspace(np.log(0.01),np.log(10**1+0.01),10, dtype=np.float32, base=np.e) - 0.01

        if np.any(['clip' in ft for ft in fitting_types]) or \
            np.any(['alexnet' in ft for ft in fitting_types]) or \
            np.any(['resnet' in ft for ft in fitting_types]):
            
            lambdas = np.logspace(np.log(0.01),np.log(10**10+0.01),20, dtype=np.float32, base=np.e) - 0.01
            
        if np.any(['semantic' in ft for ft in fitting_types]):
            # the semantic models occasionally end up with a column of all zeros, so make sure we have a 
            # small value for lambda rather than zero, to prevent issues with inverse.
            lambdas[lambdas==0] = 10e-9
            
    print('\nPossible lambda values are:')
    print(lambdas)

    return lambdas

def get_prf_models(which_grid=5, verbose=False):

    models = prf_utils.get_prf_models(which_grid=which_grid, verbose=verbose)

    return models

def most_recent_save(subject, fitting_type, n_from_end=0, root=None):     

    if root is None:
        root = default_paths.save_fits_path

    folder2load = os.path.join(root,'S%02d'%(subject), fitting_type)
     
    # within this folder, assuming we want the most recent version that was saved
    files_in_dir = os.listdir(folder2load)
    from datetime import datetime
    my_dates = [f for f in files_in_dir if 'ipynb' not in f and 'DEBUG' not in f]
    try:
        my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M_%S"))
    except:
        my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M"))
    # if n from end is not zero, then going back further in time 
    most_recent_date = my_dates[-1-n_from_end]

    return most_recent_date

def load_precomputed_prfs(subject, args):
    
    if len(args.prfs_model_name)==0 or args.prfs_model_name=='alexnet':
        # default is to use alexnet
        saved_prfs_fn = saved_fit_paths.alexnet_fit_paths[subject-1]
    elif args.prfs_model_name=='mappingtask':
        # these are just a discretized version of continuous pRF outputs, computed
        # using independent mapping task data.
        saved_prfs_fn = os.path.join(default_paths.save_fits_path,'S%02d'%subject, \
                                     'mapping_task_prfs_grid%d'%args.which_prf_grid,'prfs.npy')
    elif args.prfs_model_name=='gabor':
        saved_prfs_fn = saved_fit_paths.gabor_fit_paths[subject-1]
    elif args.prfs_model_name=='texture':
        saved_prfs_fn = saved_fit_paths.texture_fit_paths[subject-1]
    elif 'texture_fixsigma' in args.prfs_model_name:
        sigma = args.prfs_model_name.split('texture_fixsigma')[1]
        fitting_type_name = 'texture_pyramid_ridge_4ori_4sf_pca_HL_fit_pRFs_fixsigma%s'%sigma
        date = most_recent_save(subject, fitting_type_name, n_from_end=0)
        saved_prfs_fn = os.path.join(default_paths.save_fits_path, \
                                'S%02d'%subject,fitting_type_name,date,'all_fit_params.npy')
    else:
        raise ValueError('trying to load pre-computed prfs for model %s, not found'%args.prfs_model_name)

    print('Loading pre-computed pRF estimates for all voxels from %s'%saved_prfs_fn)
    out = np.load(saved_prfs_fn, allow_pickle=True).item()
    if 'prf_grid_inds' in list(out.keys()):
        best_model_each_voxel = out['prf_grid_inds'][:,0]
    else:
        assert(out['average_image_reps']==True)
        best_model_each_voxel = out['best_params'][5][:,0]
        assert(out['which_prf_grid']==args.which_prf_grid)

    return best_model_each_voxel, saved_prfs_fn

def load_best_model_layers(subject, model, dnn_layers_use):
    
    if model=='clip':
        saved_best_layer_fn = saved_fit_paths.clip_fit_paths[subject-1]
    elif model=='resnet':
        saved_best_layer_fn = saved_fit_paths.resnet50_fit_paths[subject-1]
    elif model=='resnet_blurface':
        saved_best_layer_fn = saved_fit_paths.resnet50_blurface_fit_paths[subject-1]
    elif model=='alexnet':
        saved_best_layer_fn = saved_fit_paths.alexnet_fit_paths[subject-1]
    elif model=='alexnet_blurface':
        saved_best_layer_fn = saved_fit_paths.alexnet_blurface_fit_paths[subject-1]
    else:
        raise ValueError('for %s, best model layer not computed yet'%(model))
    
    print('Loading best %s layer for all voxels from %s'%(model,saved_best_layer_fn))
    
    out = np.load(saved_best_layer_fn, allow_pickle=True).item()
    assert(out['average_image_reps']==True)
    if 'alexnet' in model:
        layer_inds = np.array([1,3,5,7,9])       
    elif ('clip' in model) or ('resnet' in model):
        if 'n_resnet_blocks_include' in out.keys() and out['n_resnet_blocks_include']==4:
            layer_inds = np.arange(1,8,2)
            dnn_layers_use = np.arange(4)
        elif 'n_resnet_blocks_include' not in out.keys() or out['n_resnet_blocks_include']==16:
            layer_inds = np.arange(1,32,2)
        else:
            raise RuntimeError('need to check inputs for resnet layers to include')
    
    print(layer_inds, dnn_layers_use)
    layer_inds_use = layer_inds[dnn_layers_use]
    assert(np.all(['just_' in name for name in np.array(out['partial_version_names'])[layer_inds]]))   
    names = [name.split('just_')[1] for name in np.array(out['partial_version_names'])[layer_inds_use]]
    print('using %s layers:'%model)
    print(names)
    
    best_layer_each_voxel = np.argmax(out['val_r2'][:,layer_inds_use], axis=1)
    unique, counts = np.unique(best_layer_each_voxel, return_counts=True)
    print('layer indices:')
    print(unique)
    print('num voxels:')
    print(counts)

    return best_layer_each_voxel, saved_best_layer_fn

def load_highlevel_labels_each_prf(subject, which_prf_grid, image_inds, models, verbose=False, debug=False):

    return label_utils.load_highlevel_labels_each_prf(subject, which_prf_grid, image_inds, models)

def load_highlevel_categ_labels_each_prf(subject, which_prf_grid, image_inds, models, verbose=False, debug=False):

    return label_utils.load_highlevel_categ_labels_each_prf(subject, which_prf_grid, image_inds, models)

def get_subsampled_trial_order(trn_image_order, \
                               holdout_image_order, \
                               val_image_order, \
                               args, index=0, \
                              trn_only=False):
    
    folder = os.path.join(default_paths.stim_labels_root,'resampled_trial_orders')
    if 'only' in args.trial_subset:        
        axis = args.trial_subset.split('_only')[0]
        fn2load = os.path.join(folder,
                   'S%d_trial_resamp_order_has_%s.npy'%\
                           (args.subject, axis))        
    elif 'balance' in args.trial_subset:       
        if 'orient' in args.trial_subset:
            axis = args.trial_subset.split('balance_orient_')[1]
            fn2load = os.path.join(folder, \
                   'S%d_trial_resamp_order_balance_4orientbins_%s.npy'%\
                           (args.subject, axis)) 
        elif 'freq' in args.trial_subset:
            axis = args.trial_subset.split('balance_freq_')[1]
            fn2load = os.path.join(folder, \
                   'S%d_trial_resamp_order_balance_2freqbins_%s.npy'%\
                           (args.subject, axis)) 
        else:            
            axis = args.trial_subset.split('balance_')[1]
            fn2load = os.path.join(folder, \
                       'S%d_trial_resamp_order_both_%s.npy'%\
                               (args.subject, axis)) 
    else:
        fn2load = os.path.join(folder, \
                   'S%d_trial_resamp_order_%s.npy'%\
                           (args.subject, args.trial_subset)) 
    print('loading balanced trial order (pre-computed) from %s'%fn2load)
    trials = np.load(fn2load, allow_pickle=True).item()
    
    if not args.debug:
        assert(np.all(trials['image_order'][trials['trninds']]==trn_image_order))
        assert(np.all(trials['image_order'][trials['valinds']]==val_image_order))
        assert(np.all(trials['image_order'][trials['outinds']]==holdout_image_order))
    
    # masks of which trials to use in each data partition (trn/val/out), 
    # for each pRF
    trn_trials_use = trials['trial_inds_trn'][:,index,:]
    val_trials_use = trials['trial_inds_val'][:,index,:]
    out_trials_use = trials['trial_inds_out'][:,index,:]
    
    # find if there are any pRFs which were left with no trials after sub-sampling.
    # if the pRF has no trials for any of the data partitions (trn/val/out), 
    # then will skip these pRFs (and voxels associated with them).
    if not trn_only:
        prf_bad_any = (np.sum(trn_trials_use, axis=0)==0) | \
                    (np.sum(val_trials_use, axis=0)==0) | \
                    (np.sum(out_trials_use, axis=0)==0)

        print('%d pRFs will be skipped due to insufficient trials'%np.sum(prf_bad_any))
        # set them to zeros so they can be skipped
        trn_trials_use[:,prf_bad_any] = 0
        val_trials_use[:,prf_bad_any] = 0
        out_trials_use[:,prf_bad_any] = 0

        # double check that there are no missing trials in unexpected places
        assert(np.all(np.sum(trn_trials_use[:,~prf_bad_any], axis=0)>0))
        assert(np.all(np.sum(val_trials_use[:,~prf_bad_any], axis=0)>0))
        assert(np.all(np.sum(out_trials_use[:,~prf_bad_any], axis=0)>0))
        assert(not np.any(np.isnan(trials['min_counts_trn'][~prf_bad_any])))
        assert(not np.any(np.isnan(trials['min_counts_val'][~prf_bad_any])))
        assert(not np.any(np.isnan(trials['min_counts_out'][~prf_bad_any])))
    else:
        prf_bad_any = (np.sum(trn_trials_use, axis=0)==0)
        print('%d pRFs will be skipped due to insufficient trials'%np.sum(prf_bad_any))
        
    return trn_trials_use, out_trials_use, val_trials_use

def load_model_residuals(args, sessions):

    subject_dir = os.path.join(default_paths.save_fits_path, 'S%02d'%args.subject)
    # load most recent file
    files_in_dir = os.listdir(os.path.join(subject_dir, args.residuals_model_name))   
    if args.debug:
        my_dates = [f for f in files_in_dir if 'ipynb' not in f and 'DEBUG' in f]
        my_dates = [dd.split('_DEBUG')[0] for dd in my_dates]
    else:
        my_dates = [f for f in files_in_dir if 'ipynb' not in f and 'DEBUG' not in f]
    try:
        my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M_%S"))
    except:
        my_dates.sort(key=lambda date: datetime.strptime(date, "%b-%d-%Y_%H%M"))
    
    try:
        most_recent_date = my_dates[-1]
    except:
        print(my_dates)
        print(os.path.join(subject_dir, args.residuals_model_name))
        raise RuntimeError('cannot find file')
        
    if args.debug:
        most_recent_date += '_DEBUG'
    residuals_dir = os.path.join(subject_dir,args.residuals_model_name,'%s'%most_recent_date)
     
    fn2load = os.path.join(residuals_dir, 'residuals_all_trials.npy')
    print('Loading single trial residuals from %s'%fn2load)
    
    out = np.load(fn2load, allow_pickle=True).item()
    assert(out['model_name']==args.residuals_model_name)
    assert(out['average_image_reps']==args.average_image_reps)
    
    voxel_data = out['residuals']
    image_order = out['image_order']
    val_inds = out['val_inds']
    session_inds = out['session_inds']
    
    is_trn, is_holdout, is_val = nsd_utils.load_image_data_partitions(args.subject)
    is_val = is_val[image_order]
    is_holdout = is_holdout[image_order]
    assert(np.all(is_val==val_inds))
    holdout_inds = is_holdout
    
    print('shape of residual voxel data is:')
    print(voxel_data.shape)
    
    # now double check that the right set of trials are here
    sessions_using = sessions[(sessions+1)<=nsd_utils.max_sess_each_subj[args.subject-1]]
    image_order_expected = nsd_utils.get_master_image_order()
    session_inds_expected = nsd_utils.get_session_inds_full()
    inds2use = np.isin(session_inds_expected, sessions_using)
    image_order_expected = image_order_expected[inds2use]
    session_inds_expected = session_inds_expected[inds2use]

    if args.average_image_reps:
        n_trials_expected = len(np.unique(image_order))
        assert(voxel_data.shape[0]==n_trials_expected)
        assert(np.all(np.unique(image_order_expected)==image_order))
    else:
        n_trials_expected = len(sessions_using)*nsd_utils.trials_per_sess
        assert(voxel_data.shape[0]==n_trials_expected)
        assert(np.all(session_inds==session_inds_expected))
        assert(np.all(image_order==image_order_expected))
    
    return voxel_data, image_order, val_inds, holdout_inds, session_inds, fn2load

def load_simul_data(args, sessions):

    if args.simul_model_name=='gabor':
        folder = os.path.join(default_paths.gabor_texture_feat_path, 'simulated_data')
    else:
        raise ValueError('simul_model_name %s not implemented yet'%args.simul_model_name)
    
    fn2load = os.path.join(folder, 'S%d_sim_data_addnoise_%.2f.npy'%(args.subject, args.simul_noise_level))
    print('Loading simulated voxel data from %s'%fn2load)
    sim_dat = np.load(fn2load,allow_pickle=True).item()
    
    voxel_data = sim_dat['sim_data']
    voxel_prf_inds = sim_dat['simulated_voxel_prf_inds']
    
    image_order = np.arange(10000)
    session_inds = None
    
    assert(args.average_image_reps)
    assert(args.subject==1)

    is_trn, is_holdout, is_val = nsd_utils.load_image_data_partitions(args.subject)
    val_inds = is_val[image_order]
    holdout_inds = is_holdout[image_order]
   
    print('shape of simulated voxel data is:')
    print(voxel_data.shape)
    
    return voxel_data, image_order, val_inds, holdout_inds, session_inds, voxel_prf_inds, fn2load



def save_model_residuals(voxel_data, voxel_data_pred, output_dir, model_name, \
                         image_order, val_inds, session_inds, \
                         all_dat_r2, args):
    
    residuals = voxel_data - voxel_data_pred
    residuals = residuals.astype(np.float32)
    
    fn2save = os.path.join(output_dir, 'residuals_all_trials.npy')
    print('Saving single trial residuals to %s'%fn2save)
    
    np.save(fn2save,{'residuals':residuals, \
                     'model_name':model_name, \
                    'image_order':image_order, \
                    'val_inds':val_inds, \
                    'session_inds':session_inds, \
                    'all_dat_r2': all_dat_r2, \
                    'average_image_reps': args.average_image_reps})
    
    
def make_feature_loaders(args, fitting_types, vi, dnn_layers_use=None):
    
    if args.image_set is None:
        sub = args.subject
        pca_subject = None
    else:
        sub = None
        pca_subject = args.subject
        
    fe = []
    fe_names = []
    for ft in fitting_types:   

        if 'gabor' in ft:
            use_noavg = ('noavg' in ft)
            if args.use_fullimage_gabor_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
            feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid,\
                                                            feature_type='gabor_solo',\
                                                            n_ori=args.n_ori_gabor, n_sf=args.n_sf_gabor,\
                                                            nonlin_fn=args.gabor_nonlin_fn, \
                                                            use_pca_feats=args.use_pca_gabor_feats, \
                                                            pca_subject = pca_subject,
                                                            use_noavg=use_noavg)
            fe.append(feat_loader)
            fe_names.append(ft)
          
        elif 'pyramid' in ft:
            feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=args.which_prf_grid, \
                                                            feature_type='pyramid_texture',\
                                                            n_ori=args.n_ori_pyr, n_sf=args.n_sf_pyr,\
                                                            pca_type=args.pyr_pca_type,\
                                                            do_varpart=args.do_pyr_varpart,\
                                                            group_all_hl_feats=args.group_all_hl_feats, \
                                                            include_solo_models=False, \
                                                            pca_subject = pca_subject)       
            fe.append(feat_loader)
            fe_names.append(ft)
            
        elif 'sketch_tokens' in ft:
            use_noavg = ('noavg' in ft)
            if args.use_fullimage_st_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
            feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='sketch_tokens',\
                                                            use_pca_feats = args.use_pca_st_feats, \
                                                            use_residual_st_feats = args.use_residual_st_feats, \
                                                            use_grayscale_st_feats = args.use_grayscale_st_feats, \
                                                            pca_subject = pca_subject,
                                                            st_pooling_size = args.st_pooling_size, \
                                                            st_use_avgpool = args.st_use_avgpool, \
                                                            use_noavg=use_noavg)
            fe.append(feat_loader)
            fe_names.append(ft)
            
        elif 'color' in ft:
            use_noavg = ('noavg' in ft)
            if args.use_fullimage_color_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
            feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='color',
                                                            pca_subject = pca_subject,
                                                            use_noavg=use_noavg)
            fe.append(feat_loader)
            fe_names.append(ft)
            
        elif 'gist' in ft:
            
            prf_grid=0
            feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            n_ori = args.n_ori_gist, \
                                                            n_blocks = args.n_blocks_gist, \
                                                            feature_type='gist')
            fe.append(feat_loader)
            fe_names.append(ft)
            
        elif 'alexnet' in ft:
            use_noavg = ('noavg' in ft)
            if args.use_fullimage_alexnet_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
            if args.alexnet_layer_name=='all_conv' or args.alexnet_layer_name=='all_layers':
                names = ['Conv%d_ReLU'%(ll) for ll in [1,2,3,4,5]]
                if args.alexnet_layer_name=='all_layers':
                    names += ['FC%d_ReLU'%(ll) for ll in [6,7]]
                print('alexnet layer_names: %s'%names)
                for ll in range(len(names)):
                    feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='alexnet',\
                                                            layer_name=names[ll],\
                                                            use_pca_feats = args.use_pca_alexnet_feats,\
                                                            padding_mode = args.alexnet_padding_mode, \
                                                            blurface = args.alexnet_blurface, \
                                                            pca_subject = pca_subject,
                                                            use_noavg=use_noavg)
                    fe.append(feat_loader)   
                    fe_names.append('alexnet_%s'%names[ll])
            elif args.alexnet_layer_name=='best_layer':
                this_layer_name = 'Conv%d_ReLU'%(vi+1)
                print(this_layer_name)
                feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='alexnet',\
                                                            layer_name=this_layer_name,\
                                                            use_pca_feats = args.use_pca_alexnet_feats,\
                                                            padding_mode = args.alexnet_padding_mode, \
                                                            blurface = args.alexnet_blurface, \
                                                            pca_subject = pca_subject,
                                                            use_noavg=use_noavg)
                fe.append(feat_loader)   
                fe_names.append(ft)
            else:
                feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='alexnet',\
                                                            layer_name=args.alexnet_layer_name,\
                                                            use_pca_feats = args.use_pca_alexnet_feats,\
                                                            padding_mode = args.alexnet_padding_mode, \
                                                            blurface = args.alexnet_blurface, \
                                                            pca_subject = pca_subject,
                                                            use_noavg=use_noavg)
                fe.append(feat_loader)
                fe_names.append(ft)

        elif 'clip' in ft or 'resnet' in ft:
            
            use_noavg = ('noavg' in ft)
            if args.use_fullimage_resnet_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
                
            if 'clip' in ft:
                training_type='clip'
            elif args.resnet_blurface:
                training_type='blurface'
            elif 'startingblurry' in ft:
                training_type = args.resnet_training_type
            else:
                training_type='imgnet'
                
            if args.resnet_layer_name=='all_resblocks':
                names = ['block%d'%(ll) for ll in dnn_layers_use]
                for ll in range(len(names)):
                    feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='resnet',layer_name=names[ll],\
                                                            model_architecture=args.resnet_model_architecture,\
                                                            use_pca_feats=args.use_pca_resnet_feats, \
                                                            training_type=training_type,
                                                            use_noavg=use_noavg,
                                                            pca_subject = pca_subject)
                    fe.append(feat_loader)   
                    fe_names.append('resnet_%s'%names[ll])
            elif args.resnet_layer_name=='best_layer':
                this_layer_name = 'block%d'%(vi)
                print(this_layer_name)
                feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='resnet',layer_name=this_layer_name,\
                                                            model_architecture=args.resnet_model_architecture,\
                                                            use_pca_feats=args.use_pca_resnet_feats, \
                                                            training_type=training_type,
                                                            use_noavg=use_noavg,
                                                            pca_subject = pca_subject)
                fe.append(feat_loader)
                fe_names.append(ft) 
            else:
                feat_loader = fwrf_features.fwrf_feature_loader(subject=sub,\
                                                            image_set=args.image_set,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_type='resnet',\
                                                            layer_name=args.resnet_layer_name,\
                                                            model_architecture=args.resnet_model_architecture,\
                                                            use_pca_feats=args.use_pca_resnet_feats, \
                                                            training_type=training_type,
                                                            use_noavg=use_noavg,
                                                            pca_subject = pca_subject)
                fe.append(feat_loader)
                fe_names.append(ft)   

        elif 'semantic' in ft:
            assert(sub is not None)
            if args.use_fullimage_sem_feats:
                prf_grid=0
            else:
                prf_grid = args.which_prf_grid
            this_feature_set = ft.split('semantic_')[1]
            
            print('semantic feature set: %s'%this_feature_set)
            feat_loader = semantic_features.semantic_feature_loader(subject=sub,\
                                                            which_prf_grid=prf_grid, \
                                                            feature_set=this_feature_set, \
                                                            remove_missing=False)
            fe.append(feat_loader)
            fe_names.append(ft)

    # Now combine subsets of features into a single module
    if len(fe)>1:
        if args.fitting_type2=='semantic' and args.fitting_type3=='':
            print('trying to compute lambda_groups')
            n_vis_fts = np.sum(['semantic' not in ft for ft in fitting_types])
            n_sem_fts = np.sum(['semantic' in ft for ft in fitting_types])
            lambda_groups = np.array([0 for ii in range(n_vis_fts)] + [1 for ii in range(n_sem_fts)])
            print(lambda_groups)
            sys.stdout.flush()
        else:
            lambda_groups = np.arange(len(fe))
        feat_loader_full = merge_features.combined_feature_loader(fe, fe_names, do_varpart = args.do_varpart,\
                                                                  include_solo_models=args.include_solo_models, 
                                                                  lambda_groups = lambda_groups)
    else:
        feat_loader_full = fe[0]
        
        
    return feat_loader_full
    
    