import glob
import os
import tifffile
import shutil

def CheckTemplateAndFix(tif_file_folder):    
    tif_file_folder=os.path.normpath(tif_file_folder)
    template_file=tif_file_folder+'/3Dreg/template.tif'    
    print(template_file)        
    file_name=os.path.basename(os.path.normpath(tif_file_folder))
    if not os.path.exists(template_file):
        shutil.copyfile(tif_file_folder+'/3Dreg/'+file_name+'_0.tif',template_file)
    else:
        try:
            test=tifffile.imread(tif_file_folder+'/3Dreg/template.tif')        
        except:
            shutil.copyfile(tif_file_folder+'/3Dreg/'+file_name+'_0.tif',template_file)
