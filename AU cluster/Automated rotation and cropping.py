import scipy
import tifffile
import numpy as np
    
tif_file="/faststorage/project/Opt_Tweezers/Brain_Gut/SBF_240828_braingut_6dpf_04_range200_step10_exposure24_power60/SBF_240828_braingut_6dpf_04_range200_step10_exposure24_power60_4D_MaxZ.tif"
Y = tifffile.imread(tif_file)
rotation_angle=-43
Y = scipy.ndimage.rotate(Y,rotation_angle, axes=(1,2))
tifffile.imsave(tif_file.replace('4D_MaxZ.tif','4D_MaxZ_rot.tif'),Y.mean(axis=0))
temp=Y.mean(axis=0).mean(axis=1)
percentile_to_remove=60
s = np.flatnonzero(temp > np.percentile(temp,percentile_to_remove))
imin, imax = s[0], s[-1]
Ycrop=Y[:,imin:imax,:]
tifffile.imsave(tif_file.replace('4D_MaxZ.tif','4D_MaxZ_rotcrop.tif'),Ycrop.mean(axis=0))
RotCropParams=[rotation_angle,percentile_to_remove,imin,imax]
np.savetxt(tif_file.replace('.tif','RotCrop.txt'),RotCropParams,delimiter=',', fmt='%f5')