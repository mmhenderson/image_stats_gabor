import numpy as np
import os
import time
import h5py

from utils import default_paths
from feature_extraction import extract_alexnet_features, extract_clip_features, texture_statistics_pyramid
from model_fitting import initialize_fitting

"""
Code to load pre-computed features from various models (gabor, alexnet, semantic, etc.)
Features have been computed at various spatial locations in a grid (pRF positions/sizes)
"""
          
class fwrf_feature_loader:
    
    def __init__(self, subject, which_prf_grid, feature_type, **kwargs):
        
        self.subject = subject            
        self.which_prf_grid = which_prf_grid
        self.init_prf_batches(kwargs)        
        self.feature_type = feature_type
        
        if self.feature_type=='gabor_solo':
            self.init_gabor_solo(kwargs)
        elif self.feature_type=='sketch_tokens':
            self.init_sketch_tokens(kwargs)
        elif self.feature_type=='pyramid_texture':
            self.init_pyramid_texture(kwargs)
        elif self.feature_type=='alexnet':
            self.init_alexnet(kwargs)
        elif self.feature_type=='clip':
            self.init_clip(kwargs)
        else:
            raise ValueError('feature type %s not recognized')

        if not os.path.exists(self.features_file):
            raise RuntimeError('Looking at %s for precomputed features, not found.'%self.features_file)

    def init_gabor_solo(self, kwargs):
        
        self.use_pca_feats = kwargs['use_pca_feats'] if 'use_pca_feats' in kwargs.keys() else False        
        self.n_ori = kwargs['n_ori'] if 'n_ori' in kwargs.keys() else 12
        self.n_sf = kwargs['n_sf'] if 'n_sf' in kwargs.keys() else 8
        self.nonlin_fn = kwargs['nonlin_fn'] if 'nonlin_fn' in kwargs.keys() else True
        
        gabor_texture_feat_path = default_paths.gabor_texture_feat_path
        if self.use_pca_feats:
            assert(self.nonlin_fn==True)
            self.features_file = os.path.join(gabor_texture_feat_path, 'PCA', \
                                          'S%d_%dori_%dsf_nonlin_PCA_grid%d.h5py'\
                                           %(self.subject, self.n_ori, self.n_sf, self.which_prf_grid))  
            with h5py.File(self.features_file, 'r') as file:
                feat_shape = np.shape(file['/features'])
                file.close()
            self.max_features = feat_shape[1]
        else:
            self.features_file = os.path.join(gabor_texture_feat_path, \
                      'S%d_features_each_prf_%dori_%dsf_gabor_solo'%(self.subject, self.n_ori, self.n_sf))
            self.max_features = self.n_ori*self.n_sf             
            if self.nonlin_fn:
                self.features_file += '_nonlin'
            self.features_file += '_grid%d.h5py'%self.which_prf_grid                                             

        self.do_varpart = False
        self.n_feature_types=1
        
    def init_pyramid_texture(self, kwargs):
        
        pyramid_texture_feat_path = default_paths.pyramid_texture_feat_path
        self.do_varpart=kwargs['do_varpart'] if 'do_varpart' in kwargs.keys() else 'True'
        self.include_ll=kwargs['include_ll'] if 'include_ll' in kwargs.keys() else 'True'
        self.include_hl=kwargs['include_hl'] if 'include_hl' in kwargs.keys() else 'True'
        self.n_ori = kwargs['n_ori'] if 'n_ori' in kwargs.keys() else 4
        self.n_sf = kwargs['n_sf'] if 'n_sf' in kwargs.keys() else 4
        self.use_pca_feats_hl=kwargs['use_pca_feats_hl'] if 'use_pca_feats_hl' in kwargs.keys() else 'True'
        self.group_all_hl_feats=kwargs['group_all_hl_feats'] if 'group_all_hl_feats' in kwargs.keys() else 'True'
        if (not self.include_ll) and (not self.include_hl):
            raise ValueError('cannot exclude both low and high level texture features.')
        if not self.include_hl:
            self.use_pca_feats_hl = False
        
        # sort out all the different sub-types of features in the texture model
        self.feature_types_all = np.array(texture_statistics_pyramid.feature_types_all)
        self.feature_type_dims_all = np.array(texture_statistics_pyramid.feature_type_dims_all)
        self.feature_is_ll = np.arange(14)<5
        self.n_ll_feats = np.sum(self.feature_type_dims_all[self.feature_is_ll])
        self.n_hl_feats = np.sum(self.feature_type_dims_all[~self.feature_is_ll])

        # Decide which of these features to include now (usually including all of them)
        if self.include_ll and self.include_hl:
            inds_include = np.ones(np.shape(self.feature_is_ll))==1          
        elif self.include_ll:
            inds_include = self.feature_is_ll==1            
        else:
            inds_include = self.feature_is_ll==0
            
        self.feature_types_include = self.feature_types_all[inds_include]
        self.feature_type_dims_include = self.feature_type_dims_all[inds_include]
        self.feature_is_ll = self.feature_is_ll[inds_include]       
        
        if self.use_pca_feats_hl:
            # get filenames/dims of the higher-level feature groups, after PCA.
            feature_dims_hl = self.feature_type_dims_include[~self.feature_is_ll]
            self.feature_names_hl = self.feature_types_include[~self.feature_is_ll]            
            self.features_files_hl = ['' for fi in range(len(feature_dims_hl))]
            self.max_pc_to_retain_hl = [0 for fi in range(len(feature_dims_hl))]
            for fi, feature_type_name in enumerate(self.feature_names_hl):
                self.features_files_hl[fi] = os.path.join(pyramid_texture_feat_path, 'PCA', \
                         'S%d_%dori_%dsf_PCA_%s_only_grid%d.h5py'%\
                         (self.subject, self.n_ori, self.n_sf, feature_type_name, self.which_prf_grid))   
                if not os.path.exists(self.features_files_hl[fi]):
                    raise RuntimeError('Looking at %s for precomputed pca features, not found.'%self.features_files_hl[fi]) 
                with h5py.File(self.features_files_hl[fi], 'r') as file:
                    feat_shape = np.shape(file['/features'])
                    file.close()
                n_feat_actual = feat_shape[1]
                self.max_pc_to_retain_hl[fi] = int(np.min([feature_dims_hl[fi], n_feat_actual]))        
            
            self.n_hl_feats = np.sum(self.max_pc_to_retain_hl)
            self.feature_type_dims_include[~self.feature_is_ll] = self.max_pc_to_retain_hl
            
        # count the number of features that we are including in the model                 
        self.n_features_total = np.sum(self.feature_type_dims_include)
        self.max_features = self.n_features_total
        
        # Numbers that define which feature types are in which columns of final output matrix
        self.feature_column_labels = np.squeeze(np.concatenate([fi*np.ones([1,self.feature_type_dims_include[fi]]) \
                                for fi in range(len(self.feature_type_dims_include))], axis=1).astype('int'))
        assert(np.size(self.feature_column_labels)==self.n_features_total)

        if self.group_all_hl_feats:
            # In this case group the smaller sets of features into just lower-level and higher-level.
            # This makes it simpler to do the variance partition analysis.
            # If do_varpart==False, this does nothing.
            self.feature_column_labels[self.feature_is_ll[self.feature_column_labels]] = 0
            self.feature_column_labels[~self.feature_is_ll[self.feature_column_labels]] = 1
            if self.include_ll and self.include_hl:
                self.feature_group_names = ['lower-level', 'higher-level']
            elif self.include_ll:
                self.feature_group_names = ['lower-level']
            elif self.include_hl:
                self.feature_group_names = ['higher-level']
        else:
            # otherwise treating each sub-set separately for variance partition.
            self.feature_group_names = self.feature_types_include

        self.n_feature_types = len(self.feature_group_names)
       
        # file that contains all lower- and higher- level feats, before PCA.
        self.features_file = os.path.join(pyramid_texture_feat_path, \
                                              'S%d_features_each_prf_%dori_%dsf_grid%d.h5py'%(self.subject, \
                                                              self.n_ori, self.n_sf, self.which_prf_grid))
        if not os.path.exists(self.features_file):
            raise RuntimeError('Looking at %s for precomputed features, not found.'%self.features_file)  

        
      
    def init_sketch_tokens(self, kwargs):

        sketch_token_feat_path = default_paths.sketch_token_feat_path

        self.use_pca_feats = kwargs['use_pca_feats'] if 'use_pca_feats' in kwargs.keys() else False
        self.use_residual_st_feats = kwargs['use_residual_st_feats'] \
                                        if 'use_residual_st_feats' in kwargs.keys() else False
           
        if self.use_pca_feats:
            self.features_file = os.path.join(sketch_token_feat_path, 'PCA', \
                                          'S%d_PCA_grid%d.h5py'%(self.subject, self.which_prf_grid))  
            with h5py.File(self.features_file, 'r') as file:
                feat_shape = np.shape(file['/features'])
                file.close()
            n_feat_actual = feat_shape[1]
            self.max_features = np.min([150, n_feat_actual]) 
        elif self.use_residual_st_feats:
            self.max_features = 150;
            self.features_file = os.path.join(sketch_token_feat_path, \
                          'S%d_gabor_residuals_grid%d.h5py'%(self.subject, self.which_prf_grid))
             
        else:
            self.max_features = 150;
            self.features_file = os.path.join(sketch_token_feat_path, \
                          'S%d_features_each_prf_grid%d.h5py'%(self.subject, self.which_prf_grid))
            
        self.do_varpart=False
        self.n_feature_types=1
    
    def init_alexnet(self,kwargs):
    
        self.padding_mode = kwargs['padding_mode'] if 'padding_mode' in kwargs.keys() else 'reflect'
        if 'layer_name' not in kwargs.keys():
            raise ValueError('for alexnet, need to specify a layer name')
        self.layer_name = kwargs['layer_name']
        self.use_pca_feats = kwargs['use_pca_feats'] if 'use_pca_feats' in kwargs.keys() else True 
        
        alexnet_feat_path = default_paths.alexnet_feat_path
        alexnet_layer_names  = extract_alexnet_features.alexnet_layer_names
        n_features_each_layer = extract_alexnet_features.n_features_each_layer

        if self.use_pca_feats:        
            self.features_file = os.path.join(alexnet_feat_path, 'PCA', \
              'S%d_%s_reflect_PCA_grid%d.h5py'%(self.subject, self.layer_name, self.which_prf_grid))
        else:
            raise RuntimeError('have to use pca feats for alexnet') 

        layer_ind = [ll for ll in range(len(alexnet_layer_names)) \
                         if alexnet_layer_names[ll]==self.layer_name]
        assert(len(layer_ind)==1)
        layer_ind = layer_ind[0]        
        n_feat_expected = n_features_each_layer[layer_ind]

        with h5py.File(self.features_file, 'r') as file:
            feat_shape = np.shape(file['/features'])
            file.close()
        n_feat_actual = feat_shape[1]
        self.max_features = np.min([n_feat_expected, n_feat_actual])

        self.do_varpart=False
        self.n_feature_types=1
        
    def init_clip(self, kwargs):
        
        self.model_architecture = kwargs['model_architecture'] if 'model_architecture' in kwargs.keys() else 'RN50'
        if 'layer_name' not in kwargs.keys():
            raise ValueError('for clip, need to specify a layer name')
        self.layer_name = kwargs['layer_name']
        self.use_pca_feats = kwargs['use_pca_feats'] if 'use_pca_feats' in kwargs.keys() else True 
        
        clip_feat_path = default_paths.clip_feat_path
        clip_layer_names  = extract_clip_features.resnet_block_names
        n_features_each_layer = extract_clip_features.n_features_each_resnet_block

        if self.use_pca_feats:
            self.features_file = os.path.join(clip_feat_path, 'PCA', \
              'S%d_%s_%s_PCA_grid%d.h5py'%(self.subject, self.model_architecture, \
                                         self.layer_name, self.which_prf_grid))  
        else:
            raise RuntimeError('have to use pca feats for clip')
            
        layer_ind = [ll for ll in range(len(clip_layer_names)) \
                         if clip_layer_names[ll]==self.layer_name]
        assert(len(layer_ind)==1)
        layer_ind = layer_ind[0]        
        n_feat_expected = n_features_each_layer[layer_ind]
           
        with h5py.File(self.features_file, 'r') as file:
            feat_shape = np.shape(file['/features'])
            file.close()
        n_feat_actual = feat_shape[1]
        self.max_features = np.min([n_feat_expected, n_feat_actual])

        self.do_varpart=False
        self.n_feature_types=1
    
    def init_prf_batches(self, kwargs):
        
        self.prf_batch_size = kwargs['prf_batch_size'] if 'prf_batch_size' in kwargs.keys() else 100
        n_prfs = initialize_fitting.get_prf_models(which_grid=self.which_prf_grid).shape[0]
        n_prf_batches = int(np.ceil(n_prfs/self.prf_batch_size))          
        self.prf_batch_inds = [np.arange(self.prf_batch_size*bb, np.min([self.prf_batch_size*(bb+1), n_prfs])) \
                               for bb in range(n_prf_batches)]
       
        self.features_each_prf_batch = None
        self.prf_inds_loaded = []
        
    def clear_big_features(self):
        
        print('Clearing features from memory')
        self.features_each_prf_batch = None 
        self.prf_inds_loaded = []
        
    def get_partial_versions(self):

        partial_version_names = ['full_model']
        masks = np.ones([1,self.max_features])
        
        if self.do_varpart and self.n_feature_types>1:

            # "Partial versions" will be listed as: [full model, model w only first set of features,
            # model w only second set, ...             
            partial_version_names += ['just_%s'%ff for ff in self.feature_group_names]
            masks2 = np.concatenate([np.expand_dims(np.array(self.feature_column_labels==ff).astype('int'), axis=0) \
                                     for ff in np.arange(0,self.n_feature_types)], axis=0)
            masks = np.concatenate((masks, masks2), axis=0)

            if self.n_feature_types > 2:
                # if more than two types, also include models where we leave out first set of features, 
                # leave out second set of features...]
                partial_version_names += ['leave_out_%s'%ff for ff in self.feature_group_names]           
                masks3 = np.concatenate([np.expand_dims(np.array(self.feature_column_labels!=ff).astype('int'), axis=0) \
                                         for ff in np.arange(0,self.n_feature_types)], axis=0)
                masks = np.concatenate((masks, masks3), axis=0)           

        return masks, partial_version_names

    def load_features_prf_batch(self, image_inds, prf_model_index):
        
        # loading features for pRFs in batches to speed up a little
        t = time.time()
        batch_to_use = np.where([prf_model_index in self.prf_batch_inds[bb] for \
                                     bb in range(len(self.prf_batch_inds))])[0][0]
        assert(prf_model_index in self.prf_batch_inds[batch_to_use])
        self.prf_inds_loaded = self.prf_batch_inds[batch_to_use]
        print('Loading pre-computed features for models [%d - %d] from %s'%\
               (self.prf_batch_inds[batch_to_use][0], self.prf_batch_inds[batch_to_use][-1], \
                self.features_file))
        self.features_each_prf_batch = None

        t = time.time()
        with h5py.File(self.features_file, 'r') as data_set:
            values = np.copy(data_set['/features'][:,:,self.prf_batch_inds[batch_to_use]])
            data_set.close() 
        elapsed = time.time() - t
        print('Took %.5f seconds to load file'%elapsed)

        if self.feature_type=='pyramid_texture':

            # just for this particular set of features, there are multiple sub-sets that need to be dealt with specially
            self.is_defined_each_prf_batch = None
            # take out just the lower-level features from here
            features_each_prf_ll = values[image_inds,0:self.n_ll_feats,:]
            is_defined_each_prf_ll = np.ones((self.n_ll_feats, len(self.prf_batch_inds[batch_to_use])),dtype=bool)

            if self.use_pca_feats_hl:

                features_each_prf_hl = np.zeros((len(image_inds), self.n_hl_feats, len(self.prf_batch_inds[batch_to_use])))
                is_defined_each_prf_hl = np.zeros((self.n_hl_feats, len(self.prf_batch_inds[batch_to_use])),dtype=bool)

                for fi, feature_type_name in enumerate(self.feature_names_hl):

                    # loading pre-computed pca features.
                    print('Loading pre-computed %s features for models [%d - %d] from %s'%\
                          (feature_type_name, \
                           self.prf_batch_inds[batch_to_use][0],self.prf_batch_inds[batch_to_use][-1],\
                           self.features_files_hl[fi]))
                    t = time.time()
                    with h5py.File(self.features_files_hl[fi], 'r') as data_set:
                        values = np.copy(data_set['/features'][:,:,self.prf_batch_inds[batch_to_use]])
                        data_set.close() 
                    elapsed = time.time() - t
                    print('Took %.5f seconds to load file'%elapsed)
                    feats_to_use = values[image_inds,:,:]
                    values = None
                    nan_inds = [np.where(np.isnan(feats_to_use[0,:,mm])) \
                                for mm in range(len(self.prf_batch_inds[batch_to_use]))]
                    nan_inds = [ni[0][0] if ((len(ni)>0) and (len(ni[0])>0)) \
                                else self.max_pc_to_retain_hl[fi] for ni in nan_inds]
                    n_feat_each_prf=nan_inds

                    start_ind = int(np.sum(self.max_pc_to_retain_hl[0:fi]))
                    print('start ind: %d'%start_ind)
                    for mm in range(len(self.prf_batch_inds[batch_to_use])):
                        features_each_prf_hl[:,start_ind:start_ind+n_feat_each_prf[mm],mm] = \
                                feats_to_use[:,0:n_feat_each_prf[mm],mm]
                        is_defined_each_prf_hl[start_ind:start_ind+n_feat_each_prf[mm],mm] = True;

            else:
                features_each_prf_hl = values[image_inds,self.n_ll_feats:,:]
                is_defined_each_prf_hl = np.ones((self.n_hl_feats, len(self.prf_batch_inds[batch_to_use])),dtype=bool)

            if self.include_ll and self.include_hl:
                self.features_each_prf_batch = np.concatenate([features_each_prf_ll, features_each_prf_hl], axis=1)
                self.is_defined_each_prf_batch = np.concatenate([is_defined_each_prf_ll, is_defined_each_prf_hl], axis=0)
            elif self.include_ll:
                self.features_each_prf_batch = features_each_prf_ll
                self.is_defined_each_prf_batch = is_defined_each_prf_ll
            elif self.include_hl:
                self.features_each_prf_batch = features_each_prf_hl
                self.is_defined_each_prf_batch = is_defined_each_prf_hl
            assert(self.features_each_prf_batch.shape[1]==self.n_features_total)

        else:
            if self.use_pca_feats:

                # if the features have been reduced with PCA, then they will have different dimension
                # for different pRFs. For lower-dim pRFs, the remaining values are filled in with nans.
                # Just using the non-nan values here.
                feats_to_use = values[image_inds,:,:]
                nan_inds = [np.where(np.isnan(feats_to_use[0,:,mm])) \
                            for mm in range(len(self.prf_batch_inds[batch_to_use]))]
                nan_inds = [ni[0][0] if ((len(ni)>0) and (len(ni[0])>0)) else self.max_features for ni in nan_inds]              
                self.features_each_prf_batch = [feats_to_use[:,0:nan_inds[mm],mm] \
                            for mm in range(len(self.prf_batch_inds[batch_to_use]))]
                values=None
                print('Length of features list this batch: %d'%len(self.features_each_prf_batch))
                print('Size of features array for first prf model with this image set is:')
                print(self.features_each_prf_batch[0].shape)

            else:

                self.features_each_prf_batch = values[image_inds,:,:]
                values = None
                self.features_each_prf_batch = self.features_each_prf_batch[:,0:self.max_features,:]
                print('Size of features array for this image set is:')
                print(self.features_each_prf_batch.shape)

    
    def load(self, image_inds, prf_model_index, fitting_mode = True):
         
        if image_inds.dtype=='bool' or np.all(np.isin(np.unique(image_inds),[0,1])):
            print('\nWARNING: image_inds (len %d) looks like a boolean array'%len(image_inds))
            print('you might need to do np.where(image_inds) first\n')
            
        if prf_model_index not in self.prf_inds_loaded:            
            self.load_features_prf_batch(image_inds, prf_model_index)
        
        # get features for the current pRF from the loaded batch 
        index_into_batch = np.where(prf_model_index==self.prf_inds_loaded)[0][0]
        print('Index into batch for prf %d: %d'%(prf_model_index, index_into_batch))
        if hasattr(self.features_each_prf_batch, 'shape'):      
            features_in_prf = self.features_each_prf_batch[:,:,index_into_batch]            
        else:
            features_in_prf = self.features_each_prf_batch[index_into_batch]
       
        assert(features_in_prf.shape[0]==len(image_inds))
        print('Size of features array for this image set and prf is:')
        print(features_in_prf.shape)
        if hasattr(self,'is_defined_each_prf_batch'):
            feature_inds_defined = self.is_defined_each_prf_batch[:,index_into_batch]
            features_in_prf = features_in_prf[:,feature_inds_defined]
        else:
            feature_inds_defined = np.zeros((self.max_features,), dtype=bool)
            feature_inds_defined[0:features_in_prf.shape[1]] = 1
        
        features = features_in_prf
        
        assert(features.shape[0]==len(image_inds))
        assert(not np.any(np.isnan(features)))
        if np.any(np.sum(features, axis=0)==0):
            print('Warning: there are columns of all zeros in features matrix, columns:')
            print(np.where(np.sum(features, axis=0)==0))
        print('Final size of feature matrix is:')
        print(features.shape)
        
        return features, feature_inds_defined