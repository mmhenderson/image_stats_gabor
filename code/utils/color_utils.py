import numpy as np
from skimage import color
import torch
import time

def srgb_to_linrgb(input_rgb):
    
    # convert from gamma-encoded sRGB to ~linear sRGB
    # input values are "gamma-compressed", the output are "gamma-expanded"
    # (this treats every color channel equally, but applies a nonlinearity to values)
    # https://en.wikipedia.org/wiki/SRGB

    lin_rgb = torch.zeros_like(input_rgb)   
    mask = input_rgb<=0.04045

    lin_rgb[mask] = input_rgb[mask]/12.92    
    lin_rgb[~mask] = ((input_rgb[~mask] + 0.055)/1.055)**2.4
    
    return lin_rgb

def rgb_to_xyz(image_rgb):
    
    # convert from RGB color space to CIE XYZ space   
    # Y in this space = Luminance
    
    # image_rgb is [h x w x colors x images]
    assert(image_rgb.shape[2]==3)
    
    # first linearize the RGB values
    lin_rgb = srgb_to_linrgb(image_rgb)
    
    rgb_to_xyz_matrix = np.array([[0.4124564, 0.3575761, 0.1804375], 
                             [0.2126729, 0.7151522, 0.0721750], 
                             [0.0193339, 0.1191920, 0.9503041]])
    
    device_use = lin_rgb.device
    rgb_to_xyz_matrix = torch.Tensor(rgb_to_xyz_matrix).to(device_use)
    
    image_xyz = torch.moveaxis(torch.tensordot(lin_rgb, rgb_to_xyz_matrix, ([2],[1])), [2],[3])
    
    return image_xyz
    

def cielab_nonlin(t):
    
    # a nonlinearity that is applied to color channels
    # when converting to CIELAB space
    # https://en.wikipedia.org/wiki/CIELAB_color_space
    
    cutoff_value = 216/24389.0 # 0.000856
    bc = t<cutoff_value # below cutoff
    ac = t>=cutoff_value # above cutoff

    # f = np.zeros_like(t)
    f = torch.zeros_like(t)
    f[bc] = t[bc]/(3*(6/29)**2) + 4/29
    f[ac] = t[ac]**(1/3.0)

    return f

def xyz_to_lab(image_xyz):
    
    # convert from CIEXYZ space to CIELAB space
    # see https://en.wikipedia.org/wiki/CIELAB_color_space
    
    assert(image_xyz.shape[2]==3)

    # these normalization values are from Standard Illuminant D65
    x_norm = image_xyz[:,:,0]*100.0/95.0489
    y_norm = image_xyz[:,:,1]*100.0/100.0
    z_norm = image_xyz[:,:,2]*100.0/108.8840

    xyz_norm = torch.stack([x_norm, y_norm, z_norm], dim=2)

    f_xyz = cielab_nonlin(xyz_norm)

    fx = f_xyz[:,:,0]
    fy = f_xyz[:,:,1]
    fz = f_xyz[:,:,2]    
    
    Lstar = 116.0 * fy - 16.0
    astar = 500.0 * (fx-fy)
    bstar = 200.0 * (fy-fz)

    image_lab = torch.stack([Lstar, astar, bstar], dim=2)
    
    return image_lab
    

def rgb_to_CIELAB(image_rgb, device=None):
    
    # full conversion from RGB space into CIE L*a*b* space
    
    assert(image_rgb.shape[2]==3)
    
    if len(image_rgb.shape)==3:
        single_image=True
        image_rgb = image_rgb[:,:,:,None]
    else:
        single_image=False
        
    if device is None:
        device = 'cpu:0'

    print('using device: %s'%device)
        
    image_rgb_tensor = torch.Tensor(image_rgb.astype(np.single)).to(device)
   
    float_rgb_tensor = image_rgb_tensor/255.0
    
    image_xyz_tensor = rgb_to_xyz(float_rgb_tensor)
   
    image_lab_tensor = xyz_to_lab(image_xyz_tensor)
   
    image_lab = image_lab_tensor.detach().cpu().numpy()
    
    if single_image:
        assert(image_lab.shape[3]==1)
        image_lab = image_lab[:,:,:,0]
        
    return image_lab

def get_saturation(image_rgb):
    
    assert(image_rgb.shape[2]==3)
    
    if len(image_rgb.shape)>3:
        batch_size = image_rgb.shape[3]
        hsv_img = np.stack([color.rgb2hsv(image_rgb[:,:,:,ii]) \
                            for ii in range(batch_size)], axis=3)
    else:
        hsv_img = color.rgb2hsv(image_rgb)

    sat_img = hsv_img[:, :, 1]
    
    return sat_img