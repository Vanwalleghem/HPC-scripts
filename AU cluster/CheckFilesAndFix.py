import glob
import os
import tifffile
from skimage import io
import numpy as np
import gc

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty    
    if os.path.exists(file_path):
        if os.stat(file_path).st_size == 0:
            return True
        else:
            return False
    else:
        return True 

def CheckFilesAndFix(tif_file_folder):
    #load and concatenate the OME.tif
    tif_list=glob.glob(tif_file_folder+'/*.tif')
    tif_list.sort()
    print('List of files is '+str(len(tif_list))+' long')
    print(tif_list)
    temp=[]
    for idx_nb,file in enumerate(tif_list):
        if idx_nb==0:
            temp=io.imread(file,plugin='pil')
        else:
            temp=np.concatenate((temp,io.imread(file,plugin='pil')),axis=0)
    #Reshape the time serie to 3D+time
    file_name=os.path.basename(os.path.normpath(tif_file_folder))
    range2=int(file_name.split('range')[-1].split('_')[0])
    step=int(file_name.split('step')[-1].split('_')[0])
    TrueSlices=int((range2/step)+1)
    print(str(TrueSlices)+' z slices')
    dims=temp.shape
    print(dims)
    temp=np.reshape(temp,[int(dims[0]/TrueSlices),TrueSlices,dims[1],dims[2]])
    gc.collect()
    new_dir=tif_file_folder+'/3Dreg'
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    for img_nb in range(0,temp.shape[0]):
        img_name=new_dir+'/'+tif_file_folder.split('/')[-1]+'_'+str(img_nb)+'.tif'
        try:
            test=tifffile.imread(img_name)
            if not test.shape==(TrueSlices,dims[1],dims[2]):
                tifffile.imsave(img_name,temp[img_nb].astype(np.uint16))
        except:
            tifffile.imsave(img_name,temp[img_nb].astype(np.uint16))
            
    del temp
    gc.collect()