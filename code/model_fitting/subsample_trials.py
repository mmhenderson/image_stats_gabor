# import basic modules
import sys
import os
import time
import numpy as np
import argparse

# import custom modules
from utils import nsd_utils, default_paths, prf_utils, label_utils
from feature_extraction import default_feature_loaders
import initialize_fitting

os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

save_path = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders')
if not os.path.exists(save_path):
    os.makedirs(save_path)
    
def get_balanced_trials(labels1, labels2, n_samp_iters=1000, \
                        unique1=None, unique2=None, rndseed=None):
    
    """
    Utility function to create a trial order balanced for two attributes.
    """
    
    if unique1 is None:
        unique1 = np.unique(labels1)
    if unique2 is None:
        unique2 = np.unique(labels2)
    unique1 = unique1[~np.isnan(unique1)]
    unique2 = unique2[~np.isnan(unique2)]
    n1 = len(unique1)
    n2 = len(unique2)
    n_bal_groups = n1*n2
   
    
    labels_balance = np.array([labels1, labels2]).T
    # list the unique combinations of the label values (groups to balance)
    combs = np.array([np.tile(unique1,[n2,]), np.repeat(unique2, n1),]).T
  
    counts_orig = np.array([np.sum(np.all(labels_balance==ii, axis=1)) \
                       for ii in combs])
    min_count = np.min(counts_orig)
    
    if min_count==0:
        print('missing at least one group of labels')
        # at least one group is missing, this won't work
        return None, None
    
    # make an array of the indices to use - [n_samp_iters x n_resampled_trials]
    trial_inds_resample = np.zeros((n_samp_iters, min_count*n_bal_groups),dtype=int)
    
    if rndseed is None:
        rndseed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rndseed)
    
    for gg in range(n_bal_groups):
        # find actual list of trials with this label combination
        trial_inds_this_comb = np.where(np.all(labels_balance==combs[gg,:], axis=1))[0]
        samp_inds = np.arange(gg*min_count, (gg+1)*min_count)
        for ii in range(n_samp_iters):
            # sample without replacement from the full set of trials.
            # if this is the smallest group, this means taking all the trials.
            # otherwise it is a sub-set of the trials.
            trial_inds_resample[ii,samp_inds] = np.random.choice(trial_inds_this_comb, \
                                                                 min_count, \
                                                                 replace=False)

    return trial_inds_resample, min_count
    
    
def make_separate_categ_labels(subject, which_prf_grid=5, \
                               n_samp_iters=1000, debug=False):
   
    """
    Create sub-sampled trial orders (within each pRF bin)
    that evenly sample from each of two binary category bins.
    """

    models = initialize_fitting.get_prf_models(which_grid = which_prf_grid)   
    n_prfs = models.shape[0]

    # figure out what images are available for this subject - assume that we 
    # will be using all the available sessions. 
    image_order = nsd_utils.get_master_image_order()    
    session_inds = nsd_utils.get_session_inds_full()
    sessions = np.arange(nsd_utils.max_sess_each_subj[subject-1])
    inds2use = np.isin(session_inds, sessions) # remove any sessions that weren't shown
    # list of all the image indices shown on each trial
    image_order = image_order[inds2use] 
    # reduce to the ~10,000 unique images
    image_order = np.unique(image_order) 

    # load the list of which images are training, holdout, and validation
    # each is a mask [~10,000] long
    is_trn, is_holdout, is_val = nsd_utils.load_image_data_partitions(subject)
    
    trninds = is_trn[image_order]
    valinds = is_val[image_order]
    outinds = is_holdout[image_order]
    
    
    n_trials = len(image_order)
    n_trn_trials = np.sum(trninds)
    n_out_trials = np.sum(outinds)
    n_val_trials = np.sum(valinds)
    
    
    # get semantic category labels
    labels_all, discrim_type_list, unique_labels_each = \
                        label_utils.load_highlevel_labels_each_prf(subject, \
                                which_prf_grid, image_inds=image_order, \
                                models=models)
    axes_to_do = [0,1,2,3]
    print('processing axes:')
    print(np.array(discrim_type_list)[axes_to_do])
    col_names = [dd.split('-') for dd in discrim_type_list]
    print(col_names)
   
    # results will be repeatable for each subject
    seeds = [361417, 401417, 441417, 481417, 511417, 551417, 591417, 31517]
    rnd_seed = seeds[int(subject-1)]
    # rnd_seed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rnd_seed)
    
    for ai, aa in enumerate(axes_to_do):

        print([ai, aa, discrim_type_list[aa]])
        
        categ_labels = labels_all[:,aa,:]
        n_categ=2;
        unique_categ = np.arange(n_categ);

        # count the minimum number of trials in any category in each pRF
        # will downsample other trials counts to match the minimum numbers
        trncounts = np.array([[np.sum(categ_labels[trninds,mm]==cat) \
                               for cat in unique_categ] for mm in range(n_prfs)])
        valcounts = np.array([[np.sum(categ_labels[valinds,mm]==cat) \
                               for cat in unique_categ] for mm in range(n_prfs)])
        outcounts = np.array([[np.sum(categ_labels[outinds,mm]==cat) \
                               for cat in unique_categ] for mm in range(n_prfs)])
        min_counts_trn = np.min(trncounts, axis=1)
        min_counts_trn -= np.mod(min_counts_trn, 2) # make sure even numbers
        min_counts_val = np.min(valcounts, axis=1)
        min_counts_val -= np.mod(min_counts_val, 2)
        min_counts_out = np.min(outcounts, axis=1)
        min_counts_out -= np.mod(min_counts_out, 2)

        # boolean masks for which trials will be included in the balanced sets
        # last dimension goes [both categ, just categ 1, just categ 2]
        trninds_mask = np.zeros((n_trn_trials,n_samp_iters,n_prfs,3), dtype=bool)
        valinds_mask = np.zeros((n_val_trials,n_samp_iters,n_prfs,3), dtype=bool)
        outinds_mask = np.zeros((n_out_trials,n_samp_iters,n_prfs,3), dtype=bool)

        for mm in range(n_prfs):

            if debug and mm>1:
                continue

            print('processing pRF %d of %d'%(mm, n_prfs))
            sys.stdout.flush()
            
            min_trials_trn = min_counts_trn[mm]
            min_trials_val = min_counts_val[mm]
            min_trials_out = min_counts_out[mm]
            
            trn_labels = categ_labels[trninds,mm]
            val_labels = categ_labels[valinds,mm]
            out_labels = categ_labels[outinds,mm]

            for xx in range(n_samp_iters):

                # start with training set labels
                has_label1 = np.where(trn_labels==0)[0]
                has_label2 = np.where(trn_labels==1)[0]

                # first, create a set of trials that has both labels represented (half of each)
                trial_inds_use1 = np.random.choice(has_label1, int(min_trials_trn/2), replace=False)
                trial_inds_use2 = np.random.choice(has_label2, int(min_trials_trn/2), replace=False)    
                trninds_mask[trial_inds_use1,xx,mm,0] = 1
                trninds_mask[trial_inds_use2,xx,mm,0] = 1

                # next, create sets of trials that are all one label    
                trial_inds_use = np.random.choice(has_label1, min_trials_trn, replace=False)
                trninds_mask[trial_inds_use,xx,mm,1] = 1    
                trial_inds_use = np.random.choice(has_label2, min_trials_trn, replace=False)
                trninds_mask[trial_inds_use,xx,mm,2] = 1

                # Then repeat for validation set
                has_label1 = np.where(val_labels==0)[0]
                has_label2 = np.where(val_labels==1)[0]

                trial_inds_use1 = np.random.choice(has_label1, int(min_trials_val/2), replace=False)
                trial_inds_use2 = np.random.choice(has_label2, int(min_trials_val/2), replace=False)    
                valinds_mask[trial_inds_use1,xx,mm,0] = 1
                valinds_mask[trial_inds_use2,xx,mm,0] = 1

                trial_inds_use = np.random.choice(has_label1, min_trials_val, replace=False)
                valinds_mask[trial_inds_use,xx,mm,1] = 1    
                trial_inds_use = np.random.choice(has_label2, min_trials_val, replace=False)
                valinds_mask[trial_inds_use,xx,mm,2] = 1

                # And repeat for holdout set
                has_label1 = np.where(out_labels==0)[0]
                has_label2 = np.where(out_labels==1)[0]

                trial_inds_use1 = np.random.choice(has_label1, int(min_trials_out/2), replace=False)
                trial_inds_use2 = np.random.choice(has_label2, int(min_trials_out/2), replace=False)    
                outinds_mask[trial_inds_use1,xx,mm,0] = 1
                outinds_mask[trial_inds_use2,xx,mm,0] = 1

                trial_inds_use = np.random.choice(has_label1, min_trials_out, replace=False)
                outinds_mask[trial_inds_use,xx,mm,1] = 1    
                trial_inds_use = np.random.choice(has_label2, min_trials_out, replace=False)
                outinds_mask[trial_inds_use,xx,mm,2] = 1

            assert(np.all(np.sum(trninds_mask[:,:,mm,:], axis=0)==min_trials_trn))
            assert(np.all(np.sum(valinds_mask[:,:,mm,:], axis=0)==min_trials_val))
            assert(np.all(np.sum(outinds_mask[:,:,mm,:], axis=0)==min_trials_out))

        # saving the results, one file per semantic axis of interest
        print([ai, aa])
        print(col_names[aa])
        groups = ['both_%s'%discrim_type_list[aa]] + col_names[aa]
        print(groups)
        for gi, gg in enumerate(groups):

            fn2save = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders', \
                               'S%d_trial_resamp_order_%s.npy'\
                                   %(subject, gg))
            print('saving to %s'%fn2save)
            np.save(fn2save, {'trial_inds_trn': trninds_mask[:,:,:,gi], \
                              'min_counts_trn': min_counts_trn, \
                              'trial_inds_val': valinds_mask[:,:,:,gi], \
                              'min_counts_val': min_counts_val, \
                              'trial_inds_out': outinds_mask[:,:,:,gi], \
                              'min_counts_out': min_counts_out, \
                              'image_order': image_order, \
                              'trninds': trninds, \
                              'valinds': valinds, \
                              'outinds': outinds, \
                              'rnd_seed': rnd_seed}, 
                    allow_pickle=True)


def make_random_downsample_sets(subject, which_prf_grid=5, \
                               n_samp_iters=1000, debug=False):
   
    """
    Create sub-sampled trial orders that have a randomly downsampled, 
    fixed number of trials.
    """

    models = initialize_fitting.get_prf_models(which_grid = which_prf_grid)   
    n_prfs = models.shape[0]

    # figure out what images are available for this subject - assume that we 
    # will be using all the available sessions. 
    image_order = nsd_utils.get_master_image_order()    
    session_inds = nsd_utils.get_session_inds_full()
    sessions = np.arange(nsd_utils.max_sess_each_subj[subject-1])
    inds2use = np.isin(session_inds, sessions) # remove any sessions that weren't shown
    # list of all the image indices shown on each trial
    image_order = image_order[inds2use] 
    # reduce to the ~10,000 unique images
    image_order = np.unique(image_order) 

    # load the list of which images are training, holdout, and validation
    # each is a mask [~10,000] long
    is_trn, is_holdout, is_val = nsd_utils.load_image_data_partitions(subject)
    
    trninds = is_trn[image_order]
    valinds = is_val[image_order]
    outinds = is_holdout[image_order]
        
    n_trials = len(image_order)
    n_trn_trials = np.sum(trninds)
    n_out_trials = np.sum(outinds)
    n_val_trials = np.sum(valinds)
    
    rnd_seed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rnd_seed)
    
    pct_keep_list = np.array(list(np.arange(0.02, 0.10, 0.02)) + list(np.arange(0.10, 1, 0.10)))
    for pct_keep in pct_keep_list:
        
        min_trials_trn = int(np.round(n_trn_trials*pct_keep))
        min_trials_val = int(np.round(n_val_trials*pct_keep))
        min_trials_out = int(np.round(n_out_trials*pct_keep))
        print('pct %.2f, keeping n trials:'%pct_keep)
        print([min_trials_trn, min_trials_val, min_trials_out])
        sys.stdout.flush()
            
        # boolean masks for which trials will be included after downsampling
        trninds_mask = np.zeros((n_trn_trials,n_samp_iters,n_prfs), dtype=bool)
        valinds_mask = np.zeros((n_val_trials,n_samp_iters,n_prfs), dtype=bool)
        outinds_mask = np.zeros((n_out_trials,n_samp_iters,n_prfs), dtype=bool)

        for ii in range(n_samp_iters):
            
            # just randomly choose a set of trials to use
            trninds_use = np.random.choice(np.arange(n_trn_trials), min_trials_trn, replace=False)
            trninds_mask[trninds_use,ii,:] = 1
            valinds_use = np.random.choice(np.arange(n_val_trials), min_trials_val, replace=False)
            valinds_mask[valinds_use,ii,:] = 1
            outinds_use = np.random.choice(np.arange(n_out_trials), min_trials_out, replace=False)
            outinds_mask[outinds_use,ii,:] = 1
        
        fn2save = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders', \
                                   'S%d_trial_resamp_order_random_downsample_%.2f.npy'%(subject, pct_keep))
        print('saving to %s'%fn2save)
        np.save(fn2save, {'trial_inds_trn': trninds_mask, \
                          'min_counts_trn': min_trials_trn*np.ones((n_prfs,)), \
                          'trial_inds_val': valinds_mask, \
                          'min_counts_val': min_trials_val*np.ones((n_prfs,)), \
                          'trial_inds_out': outinds_mask, \
                          'min_counts_out': min_trials_out*np.ones((n_prfs,)), \
                          'image_order': image_order, \
                          'trninds': trninds, \
                          'valinds': valinds, \
                          'outinds': outinds, \
                          'rnd_seed': rnd_seed}, 
                allow_pickle=True)


def make_decoding_subsets_balanced_matchprfs(subject=999, which_prf_grid=5, \
                               n_samp_iters=1000, debug=False):
   
    """
    Creating balanced subsets of images to use for the feature decoding analysis
    (decode category from features, no neural data used).
    Criteria are that for each semantic axis, the subsets of images should have 50% each label
    and should have the same num trials for each pRF (to make pRF comparisons fair).
    """

    
    # load this file that has the "counts" of every high-level semantic label, 
    # in every pRF. Need to know the minimum number for any pRF, 
    # so that we can equalize across pRFs.
    counts_filename = os.path.join(default_paths.stim_labels_root, 'Highlevel_counts_all.npy')
    counts = np.load(counts_filename, allow_pickle=True).item()
    
    models = prf_utils.get_prf_models(which_grid=which_prf_grid)
    prfs_use = prf_utils.get_prfs_use_decoding(which_prf_grid=which_prf_grid)
    n_prfs = len(prfs_use)
    print('using %d of %d pRFs'%(np.sum(prfs_use), n_prfs))
    
    if subject==999:
        # 999 is a code for the independent coco image set, using all images
        # (cross-validate within this set)
        n_images = 10000
        sub_ind = 8
    elif subject==998:
        # this is the larger set of 50,000 independent images
        n_images = 50000
        sub_ind = 9
    else:
        raise ValueError('subject must be 999 or 998')
    
    image_order = np.arange(n_images)
    
    counts_each = counts['counts_binary'][sub_ind,prfs_use,:,:]
    assert(np.sum(counts_each[0,0,:])==n_images)
    min_counts_each_prf = np.min(counts_each[:,:,0:2], axis=2)
    min_counts = np.min(min_counts_each_prf, axis=0).astype(int)
    
    # same fixed number of trials for all axes, and for all pRFs that we're including
    n_each = np.min(min_counts)
    
    n_trials = len(image_order)

    # get semantic category labels
    labels_all, discrim_type_list, unique_labels_each = \
                        label_utils.load_highlevel_labels_each_prf(subject, \
                                which_prf_grid, image_inds=image_order, \
                                models=models)

    rnd_seed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rnd_seed)

    axes_to_do = np.arange(len(discrim_type_list))
    for ai, aa in enumerate(axes_to_do):


        axis_name = counts['axis_names'][ai]

        print([ai, aa, axis_name])

        # get labels for axis of interest
        categ_labels = labels_all[:,aa,:]

        # how many trials minimum any group, any pRF?
        # n_each = min_counts[ai]
        print(n_each)
    
        # boolean masks for which trials will be included in the balanced sets
        # the sets are each balanced perfectly for label 1 & label 2, with
        # no ambiguous trials.
        inds_mask = np.zeros((n_trials,n_samp_iters,n_prfs), dtype=bool)

        for mm in range(n_prfs):

            if not prfs_use[mm]:
                continue
                
            if debug and mm>1:
                continue

            print('processing pRF %d of %d'%(mm, n_prfs))
            sys.stdout.flush()

            labels = categ_labels[:,mm]

            for xx in range(n_samp_iters):

                # find trials w each label
                has_label1 = np.where(labels==0)[0]
                has_label2 = np.where(labels==1)[0]

                # create a set of trials that has both labels represented (half of each)
                trial_inds_use1 = np.random.choice(has_label1, n_each, replace=False)
                trial_inds_use2 = np.random.choice(has_label2, n_each, replace=False)    
                inds_mask[trial_inds_use1,xx,mm] = 1
                inds_mask[trial_inds_use2,xx,mm] = 1

            assert(np.all(np.sum(inds_mask[:,:,mm], axis=0)==n_each*2))

        # save these re-sampled trial orders, to load later on
        fn2save = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders', \
                           'S%d_balance_%s_for_decoding_matchprfs.npy'\
                               %(subject, axis_name))
        print('saving to %s'%fn2save)
        np.save(fn2save, {'trial_inds_balanced': inds_mask, \
                          'image_order': image_order, \
                          'axis_names': axis_name, \
                          'rnd_seed': rnd_seed, \
                          'min_counts': min_counts}, 
                allow_pickle=True)
     
def make_decoding_categ_subsets_balanced_matchprfs(subject=999, which_prf_grid=5, \
                               n_samp_iters=1000, debug=False):
   
    # load this file that has the "counts" of every high-level semantic label, 
    # in every pRF. Need to know the minimum number for any pRF, 
    # so that we can equalize across pRFs.
    counts_filename = os.path.join(default_paths.stim_labels_root, 'Highlevel_counts_all.npy')
    counts = np.load(counts_filename, allow_pickle=True).item()
    
    models = prf_utils.get_prf_models(which_grid=which_prf_grid)
    prfs_use = prf_utils.get_prfs_use_decoding(which_prf_grid=which_prf_grid)
    n_prfs = len(prfs_use)
    print('using %d of %d pRFs'%(np.sum(prfs_use), n_prfs))
    
    if subject==999:
        # 999 is a code for the independent coco image set, using all images
        # (cross-validate within this set)
        n_images = 10000
        sub_ind = 8
    elif subject==998:
        # this is the larger set of 50,000 independent images
        n_images = 50000
        sub_ind = 9
    else:
        raise ValueError('subject must be 999 or 998')
    
    image_order = np.arange(n_images)
    
    counts_each = counts['counts_categ'][sub_ind,prfs_use,:]
    min_counts_each_prf = counts_each
    min_counts = np.min(min_counts_each_prf, axis=0).astype(int)
    
    # same fixed number of trials for all axes, and for all pRFs that we're including
    n_each = np.min(min_counts)
    
    n_trials = len(image_order)

    # get semantic category labels
    labels_all, categ_list = label_utils.load_highlevel_categ_labels_each_prf(subject, \
                                which_prf_grid, image_inds=image_order, \
                                models=models)

    rnd_seed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rnd_seed)

    axes_to_do = np.arange(len(categ_list))
    for ai, aa in enumerate(axes_to_do):

        axis_name = counts['categ_names'][ai]

        print([ai, aa, axis_name])

        # get labels for axis of interest
        categ_labels = labels_all[:,aa,:]

        # how many trials minimum any group, any pRF?
        # n_each = min_counts[ai]
        print(n_each)
    
        # boolean masks for which trials will be included in the balanced sets
        # the sets are each balanced perfectly for label 1 & label 2, with
        # no ambiguous trials.
        inds_mask = np.zeros((n_trials,n_samp_iters,n_prfs), dtype=bool)

        for mm in range(n_prfs):

            if not prfs_use[mm]:
                continue
                
            if debug and mm>1:
                continue

            print('processing pRF %d of %d'%(mm, n_prfs))
            sys.stdout.flush()

            labels = categ_labels[:,mm]

            for xx in range(n_samp_iters):

                # find trials w each label
                has_label1 = np.where(labels==0)[0]
                has_label2 = np.where(labels==1)[0]

                # create a set of trials that has both labels represented (half of each)
                trial_inds_use1 = np.random.choice(has_label1, n_each, replace=False)
                trial_inds_use2 = np.random.choice(has_label2, n_each, replace=False)    
                inds_mask[trial_inds_use1,xx,mm] = 1
                inds_mask[trial_inds_use2,xx,mm] = 1

            assert(np.all(np.sum(inds_mask[:,:,mm], axis=0)==n_each*2))

        # save these re-sampled trial orders, to load later on
        fn2save = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders', \
                           'S%d_balance_categ_%s_for_decoding_matchprfs.npy'\
                               %(subject, axis_name))
        print('saving to %s'%fn2save)
        np.save(fn2save, {'trial_inds_balanced': inds_mask, \
                          'image_order': image_order, \
                          'axis_names': axis_name, \
                          'rnd_seed': rnd_seed, \
                          'min_counts': min_counts}, 
                allow_pickle=True)
     

def make_decoding_subsets_balanced(subject=999, which_prf_grid=5, \
                               n_samp_iters=1000, debug=False):
   
    """
    Creating balanced subsets of images to use for the feature decoding analysis
    (decode category from features, no neural data used).
    Criteria are that for each semantic axis, the subsets of images should have 50% each label
    and should have the same num trials for each pRF (to make pRF comparisons fair).
    """
    
    # load this file that has the "counts" of every high-level semantic label, 
    # in every pRF. Need to know the minimum number for any pRF, 
    # so that we can equalize across pRFs.
    counts_filename = os.path.join(default_paths.stim_labels_root, 'Highlevel_counts_all.npy')
    counts = np.load(counts_filename, allow_pickle=True).item()
    
    models = prf_utils.get_prf_models(which_grid=which_prf_grid)
    n_prfs = models.shape[0]
    
    if subject==999:
        # 999 is a code for the independent coco image set, using all images
        # (cross-validate within this set)
        n_images = 10000
        sub_ind = 8
    elif subject==998:
        # this is the larger set of 50,000 independent images
        n_images = 50000
        sub_ind = 9
    else:
        raise ValueError('subject must be 999 or 998')
    
    image_order = np.arange(n_images)
    
    counts_each = counts['counts_binary'][sub_ind,:,:,:]
    assert(np.sum(counts_each[0,0,:])==n_images)
    min_counts_each_prf = np.min(counts_each[:,:,0:2], axis=2)
    print(min_counts_each_prf.shape)
   
    n_trials = len(image_order)

    # get semantic category labels
    labels_all, discrim_type_list, unique_labels_each = \
                        label_utils.load_highlevel_labels_each_prf(subject, \
                                which_prf_grid, image_inds=image_order, \
                                models=models)

    rnd_seed = int(time.strftime('%M%H%d', time.localtime()))
    np.random.seed(rnd_seed)

    axes_to_do = np.arange(len(discrim_type_list))
    for ai, aa in enumerate(axes_to_do):

        axis_name = counts['axis_names'][ai]

        print([ai, aa, axis_name])

        # get labels for axis of interest
        categ_labels = labels_all[:,aa,:]

        # boolean masks for which trials will be included in the balanced sets
        # the sets are each balanced perfectly for label 1 & label 2, with
        # no ambiguous trials.
        inds_mask = np.zeros((n_trials,n_samp_iters,n_prfs), dtype=bool)

        for mm in range(n_prfs):

            if debug and mm>1:
                continue

            print('processing pRF %d of %d'%(mm, n_prfs))
            sys.stdout.flush()
            
            # how many trials minimum any group?
            n_each = int(min_counts_each_prf[mm,ai])
            print(n_each)

            labels = categ_labels[:,mm]

            for xx in range(n_samp_iters):

                # find trials w each label
                has_label1 = np.where(labels==0)[0]
                has_label2 = np.where(labels==1)[0]

                # create a set of trials that has both labels represented (half of each)
                trial_inds_use1 = np.random.choice(has_label1, n_each, replace=False)
                trial_inds_use2 = np.random.choice(has_label2, n_each, replace=False)    
                inds_mask[trial_inds_use1,xx,mm] = 1
                inds_mask[trial_inds_use2,xx,mm] = 1

            assert(np.all(np.sum(inds_mask[:,:,mm], axis=0)==n_each*2))

        # save these re-sampled trial orders, to load later on
        fn2save = os.path.join(default_paths.stim_labels_root, 'resampled_trial_orders', \
                           'S%d_balance_%s_for_decoding.npy'\
                               %(subject, axis_name))
        print('saving to %s'%fn2save)
        np.save(fn2save, {'trial_inds_balanced': inds_mask, \
                          'image_order': image_order, \
                          'axis_names': axis_name, \
                          'rnd_seed': rnd_seed,\
                          'min_counts_each_prf': min_counts_each_prf}, 
                allow_pickle=True)
     
        
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--subject", type=int,default=1,
                    help="number of the subject, 1-8")
    parser.add_argument("--n_samp_iters", type=int,default=1000,
                    help="how many balanced trial orders to create?")
    parser.add_argument("--which_prf_grid", type=int,default=5,
                    help="which grid of candidate prfs?")     
    parser.add_argument("--debug",type=int,default=0,
                    help="want to run a fast test version of this script to debug? 1 for yes, 0 for no")

    parser.add_argument("--separate_categ",type=int,default=0,
                    help="want to create labels of one semantic category at a time? 1 for yes, 0 for no")
    parser.add_argument("--random_downsample",type=int,default=0,
                    help="want to create subsets with random downsampling? 1 for yes, 0 for no")
    parser.add_argument("--balance_for_decoding",type=int,default=0,
                    help="want to balance images for image decoding analysis? 1 for yes, 0 for no")
    parser.add_argument("--balance_for_decoding_matchprfs",type=int,default=0,
                    help="want to balance images for image decoding analysis? 1 for yes, 0 for no")
    parser.add_argument("--balance_categ_for_decoding_matchprfs",type=int,default=0,
                    help="want to balance images for image decoding analysis? 1 for yes, 0 for no")
    
    args = parser.parse_args()

    if args.separate_categ:
        make_separate_categ_labels(args.subject, args.which_prf_grid, \
                                 debug=args.debug==1, \
                                 n_samp_iters=args.n_samp_iters)
    
    if args.random_downsample:
        make_random_downsample_sets(args.subject, args.which_prf_grid, \
                                 n_samp_iters=args.n_samp_iters)
        
    
    if args.balance_for_decoding_matchprfs:
        make_decoding_subsets_balanced_matchprfs(args.subject, args.which_prf_grid, \
                                       n_samp_iters=args.n_samp_iters, debug=args.debug==1)
    
    if args.balance_categ_for_decoding_matchprfs:
        make_decoding_categ_subsets_balanced_matchprfs(args.subject, args.which_prf_grid, \
                                       n_samp_iters=args.n_samp_iters, debug=args.debug==1)
       
    if args.balance_for_decoding:
        make_decoding_subsets_balanced(args.subject, args.which_prf_grid, \
                                      n_samp_iters=args.n_samp_iters, debug=args.debug==1)