from subprocess import call
import time
import glob
import os
import sys
import tifffile
from skimage import io
import numpy as np
import nibabel as nib
import multiprocessing as mp
from scipy import signal
import gc

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0
    
def Register_single_image(Mov_name,template_name):        
    output_name = Mov_name.replace('.tif','_LongReg')      
    if not os.path.exists(output_name+'.nii') and is_file_empty(output_name+'.nii'):
        #job_string = "antsRegistration -d 3 --float 1 -o [OutImg, OutImg.nii] -n WelchWindowedSinc -w [0.005,0.995] -u 1 -r [FixImg,MovImg, 1] -t rigid[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x200x50,1e-7,5] -f 8x4x2x1 -s 2x1x1x0vox -t Affine[0.1] -m MI[FixImg,MovImg,1,32, Regular,0.25] -c [1000x500x200x50,1e-7,5] -f 8x4x2x1 -s 2x1x1x0vox -t SyN[0.05,6,0.5] -m CC[FixImg,MovImg,1,2] -c [100x500x200x50,1e-7,5] -f 8x4x2x1 -s 2x2x1x0vox -v 0"    
        job_string = "antsRegistration -d 3 --float 1 -o [OutImg,OutImg.nii] -n WelchWindowedSinc -w [0.05,0.95]  -u 0 - r [FixImg,MovImg] -t Rigid[0.1] -m MI[FixImg,MovImg,1,32,Regular,0.25] -c 500x200x100x50 -f 8x4x2x1 -s 3x2x1x0 -t Affine[0.1] -m MI[FixImg,MovImg,1,32,Regular,0.25] -c 500x200x100x50 -f 8x4x2x1 -s 3x2x1x0 -t SyN[0.1] -m CC[FixImg,MovImg,1,2] -c 100x50x20x10 -f 8x4x2x1 -s 3x2x1x0 -v 1"        
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        call([job_string],shell=True)     

def MakeListAndHyperstack(tif_file_folder):
    tif_list=glob.glob(tif_file_folder+'/*.tif')
    tif_list.sort()
    if not (os.path.exists(tif_file_folder+'/3Dreg/template.tif') and not is_file_empty(tif_file_folder+'/3Dreg/'+tif_file_folder.split('/')[-2]+'_0.tif')):
        temp=[]
        for idx_nb,file in enumerate(tif_list):
            if idx_nb==0:
                temp=io.imread(file,plugin='pil')
            else:
                temp=np.concatenate((temp,io.imread(file,plugin='pil')),axis=0)
            
        file_name=tif_file_folder.split('/')[-1]
        range2=int(file_name.split('range')[-1].split('_')[0])
        step=int(file_name.split('step')[-1].split('_')[0])
        TrueSlices=(range2/step)+1;
        dims=temp.shape
        temp=np.reshape(temp,[dims[0]/TrueSlices,TrueSlices,dims[1],dims[2]])

        #Computing the difference between points from frame to frame should give the point with least changes
        #std_movie=temp[:,0:200].std(axis=(2,3))
        number_of_frames_to_check=50
        std_movie=np.diff(temp[0:number_of_frames_to_check].reshape([number_of_frames_to_check,temp.shape[1],temp.shape[2]*temp.shape[3]]),axis=-1)
        idx_template=np.argmin(std_movie,axis=0)
        #ignores the 0s and compute the mean index of the lowest changes
        idx_template=int(idx_template[idx_template>0].ravel().mean())

        #tmp_idx=np.argmin(signal.detrend(std_movie))
        #mean image of the 3 points surrounding the minimum movement
        template=temp[idx_template-1:idx_template+2].mean(axis=0)
        directory = os.getcwd()
        try:
            new_dir=tif_file_folder+'/3Dreg'
            os.mkdir(new_dir)
        except:
            print('directory exists')
            
        os.chdir(new_dir)
        template_name=new_dir+'/template.tif'
        tifffile.imsave(template_name,template.astype(np.uint16))
        img_seq_list=list()
         
        for img_nb in range(0,temp.shape[0]):
            img_name=new_dir+'/'+tif_file_folder.split('/')[-1]+'_'+str(img_nb)+'.tif'
            tifffile.imsave(img_name,temp[img_nb].astype(np.uint16))
            img_seq_list.append(img_name)
        del temp,std_movie
        gc.collect()
    return(tif_list)

tif_file_folder=sys.argv[1]
os.chdir(os.path.dirname(tif_file_folder))
N = 2 #int((mp.cpu_count()/4)-2)
tif_list=glob.glob(tif_file_folder+'/*.tif')
tif_list.sort()

tif_list=MakeListAndHyperstack(tif_file_folder)
img_seq_list=glob.glob(tif_file_folder+'/3Dreg/*.tif')
template_name=tif_file_folder+'/3Dreg/template.tif'
p=mp.Pool(processes = N)
result=[p.apply_async(Register_single_image, (img_name,template_name)) for img_name in img_seq_list]
for ind_result in result:
    ind_result.get()

    
#with doesn't work in 2.7 for mp
#with mp.Pool(processes = N) as p:
    #for img_nb in range(0,temp.shape[0]):
     #   img_name=tif_file.replace('.tif','_'+'{:0>5}'.format(img_nb)+'.tif').replace(directory,new_dir+'/')
      #  result=p.apply(Register_single_image, (img_name,template_name))

# list_img = glob.glob(new_dir+'/*Reg.nii')    
# list_img.sort()
# name=list_img[0]    
# base_img=nib.load(name)
# base_img=np.squeeze(np.asarray(base_img.get_fdata(),dtype='float32'))
# frames=np.zeros((len(list_img),base_img.shape[1],base_img.shape[0]), dtype='uint16')
# for img_nb,C1_name in enumerate(list_img):    
    # img_temp=nib.load(C1_name)
    # img_temp=img_temp.get_fdata()    
    # img_temp=np.squeeze(np.asarray(img_temp,dtype='uint16'))
    # frames[img_nb,:,:]=np.flipud(np.rot90(img_temp,1))    
# tifffile.imsave(name.replace('.nii','_3D.tif'),frames)
