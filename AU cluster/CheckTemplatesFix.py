import glob
import os
import tifffile
from skimage import io
import numpy as np
import shutil

def CheckTemplateAndFix(tif_file_folder):
    #load and concatenate the OME.tif
    template_file=glob.glob(tif_file_folder+'/3Dreg/template.tif')
    template_file.sort()
    print(template_file)    
    #Reshape the time serie to 3D+time
    file_name=os.path.basename(os.path.normpath(tif_file_folder))
    if is_file_empty(template_file):
        shutil.copyfile(tif_file_folder+'/3Dreg/'file_name+'_0.tif',tif_file_folder+'/3Dreg/template.tif')
    else:
        try:
            test=tifffile.imread(tif_file_folder+'/3Dreg/template.tif')        
        except:
            shutil.copyfile(tif_file_folder+'/3Dreg/'file_name+'_0.tif',tif_file_folder+'/3Dreg/template.tif')