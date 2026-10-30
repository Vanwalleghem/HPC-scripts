import subprocess
import glob
import os
import re
import sys
import tifffile
import numpy as np
import nibabel as nib
import natsort
from scipy.ndimage import uniform_filter
EXPECTED_FRAME_COUNT = 1200

def run_command(job_string):
    """
    Execute a shell command and raise an exception if it fails.

    Parameters
    ----------
    job_string : str
        Command to execute.
    """
    print(job_string)
    subprocess.run(
        job_string,
        shell=True,
        check=True
    )

def is_file_empty(file_path):
    """
    Return True if file does not exist or has zero size.
    """
    if not os.path.exists(file_path):
        return True
    return os.stat(file_path).st_size == 0

def extract_range_step(file_name):
    """
    Extract range and step values from filenames.

    Example
    -------
    sample_range130_step5_time001.tif

    Returns
    -------
    range2 : int
    step : int
    """
    match = re.search(
        r"range(\d+)_step(\d+)",
        file_name)
    if match is None:
        raise ValueError(
            f"Could not parse range/step from filename: "
            f"{file_name}")
    range2 = int(match.group(1))
    step = int(match.group(2))
    if step == 0:
        raise ValueError(
            f"step cannot be zero: {file_name}")
    return range2, step

def compute_ncc(img1, img2):
    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)
    img1 -= img1.mean()
    img2 -= img2.mean()
    numerator = np.sum(img1 * img2)
    denominator = (np.sqrt(np.sum(img1**2))* np.sqrt(np.sum(img2**2)))
    if denominator == 0:
        return 0.0
    return numerator / denominator

def masked_rmse(template, warped, mask):

    diff = (template[mask > 0]- warped[mask > 0])
    return np.sqrt(np.mean(diff**2))

def compute_wncc_fast(
        img1,
        img2,
        mask=None,
        window_size=(32, 32, 8),
        eps=1e-8):
    """
    Fast Windowed NCC using local statistics.

    Parameters
    ----------
    img1 : ndarray
        Template volume

    img2 : ndarray
        Warped volume

    mask : ndarray or None
        Mask limiting evaluation region

    window_size : tuple
        Local NCC window size

    eps : float
        Prevent division by zero

    Returns
    -------
    wncc_mean : float

    wncc_map : ndarray
        Local NCC value at every voxel
    """

    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)

    if mask is None:
        mask = np.ones_like(img1, dtype=bool)
    else:
        mask = mask > 0

    mean1 = uniform_filter(
        img1,
        size=window_size,
        mode="nearest"
    )

    mean2 = uniform_filter(
        img2,
        size=window_size,
        mode="nearest"
    )

    mean12 = uniform_filter(
        img1 * img2,
        size=window_size,
        mode="nearest"
    )

    mean11 = uniform_filter(
        img1 * img1,
        size=window_size,
        mode="nearest"
    )

    mean22 = uniform_filter(
        img2 * img2,
        size=window_size,
        mode="nearest"
    )

    cov12 = mean12 - mean1 * mean2

    var1 = mean11 - mean1 * mean1
    var2 = mean22 - mean2 * mean2

    denominator = np.sqrt(
        np.maximum(var1, 0) *
        np.maximum(var2, 0)
    ) + eps

    wncc_map = cov12 / denominator

    wncc_mean = float(
        np.mean(wncc_map[mask])
    )

    return wncc_mean, wncc_map


def Register_single_image_SecondPass(Mov_name,template_name,Mask_name):        
 output_name = Mov_name.replace('_Warp1.nii.gz','_orig2').replace('_orig.nii.gz','.tif_orig2').replace('.tif.tif','.tif')
 if is_file_empty(output_name+'.nii.gz'):   
  job_string = "greedy -d 3 -float -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -mm MaskImg -sv -n 300x150x50 -e 0.25 -m NCC 2x2x2"
  job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  run_command(job_string)
 output_image = Mov_name.replace('_Warp1.nii.gz','_Warp2')
 if is_file_empty(output_image+'.nii.gz'):
  job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
  job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
  run_command(job_string)

def Register_single_image_noMask_SecondPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warp1.nii.gz','_orig2')    
    file_name=os.path.basename(Mov_name)
    if is_file_empty(output_name+'.nii.gz'):        
        range2, step = extract_range_step(file_name)
        TrueSlices = (range2 / step) + 1
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 200x100x50 -e 0.25 -m NCC 2x2x2"
        else:
            job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 300x100 -e 0.25 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        run_command(job_string)
    output_image = Mov_name.replace('_Warp1.nii.gz','_Warp2')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        run_command(job_string)

def Register_single_image_ThirdPass(Mov_name,template_name):        
    output_name = Mov_name.replace('_Warp2.nii.gz','_orig3')    
    if is_file_empty(output_name+'.nii.gz'):
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -sv -n 200x100x50 -e 0.15 -m NCC 2x2x2"
        job_string = job_string.replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        run_command(job_string)
    output_image = Mov_name.replace('_Warp2.nii.gz','_Warp3')
    if is_file_empty(output_image+'.nii.gz'):    
        job_string = "greedy -d 3 -rf FixImg -rm MovImg OutImg.nii.gz -r "+output_name+'.nii.gz'
        job_string = job_string.replace('OutImg',output_image).replace('FixImg',template_name).replace('MovImg',Mov_name)
        run_command(job_string)

def Register_single_image(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_orig')
    Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
    if not os.path.exists(Affine_name) and is_file_empty(output_name+'.nii.gz'):        
        output_name = Mov_name.replace('.tif','_orig') 
        Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
        file_name=os.path.basename(Mov_name)
        range2, step = extract_range_step(file_name)
        TrueSlices = (range2 / step) + 1
        if TrueSlices >= 16:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -n 300x200x150 -e 0.5 -ia-identity -m NCC 3x3x2"
        else:
            job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -n 300x200x150 -e 0.5 -ia-identity -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name)
        run_command(job_string)  
        print(job_string)
        #if TrueSlices >= 16:
        #    job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -sv -n 300x150x80 -e 0.5  -m NCC 3x3x2"
        #else:
        job_string = "greedy -d 3 -s 1.8vox 1vox -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -mm MaskImg -it Affine_name -sv -n 300x150x80 -e 0.5 -m NCC 3x3x2"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        run_command(job_string)  
        job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warp1.nii.gz -r OutImg.nii.gz Affine_name"
        job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
        run_command(job_string)

def FindTemplate(tif_file_folder, number_of_frames_to_check=50):
    """Return the TIFF (among the first N frames) that changes least relative to its neighbours."""
    new_dir = os.path.join(tif_file_folder, '3Dreg')
    files = natsort.natsorted(glob.glob(os.path.join(new_dir, '*_time*.tif')))
    if not files:
        files = natsort.natsorted(glob.glob(os.path.join(new_dir, '*.tif')))
    files = [f for f in files if 'arped' not in f and 'template' not in f.lower() and '_Warp' not in f]
    files = files[:number_of_frames_to_check]
    if len(files) < 2:
        raise ValueError(f'Need at least 2 TIFFs in {new_dir} to pick a template, found {len(files)}')
    ref_shape = None
    prev = None
    scores = np.zeros(len(files), dtype=np.float32)  # worst change to an adjacent frame

    for i, f in enumerate(files):
        vol = tifffile.imread(f)
        if ref_shape is None:
            ref_shape = vol.shape
        elif vol.shape != ref_shape:
            vol = np.transpose(vol, axes=(2, 0, 1))      # your original fallback
            if vol.shape != ref_shape:
                raise ValueError(f'{f}: shape {vol.shape} does not match {ref_shape}')
        vol = vol.astype(np.float32)

        if prev is not None:
            d = float(np.max(np.abs(vol - prev)))
            scores[i] = max(scores[i], d)
            scores[i - 1] = max(scores[i - 1], d)
        prev = vol

    return files[int(np.argmin(scores))]


def Register_single_image_forced(Mov_name,template_name,Mask_name):        
    output_name = Mov_name.replace('.tif','_orig').replace('3Dreg','3Dreg2')
    Affine_name = Mov_name.replace('.tif','_orig_affine.mat')
    file_name=os.path.basename(Mov_name)
    range2, step = extract_range_step(file_name)
    TrueSlices = (range2 / step) + 1
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 200x80x40 -e 0.5 -ia-image-centers -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -a -o Affine_name -i FixImg MovImg -gm MaskImg -n 300x100 -e 0.5 -ia-image-centers -m NCC 3x3x2"    
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    run_command(job_string)  
    print(job_string)
    if TrueSlices >= 16:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 200x80x40 -e 0.5 -m NCC 3x3x2"
    else:
        job_string = "greedy -d 3 -o OutImg.nii.gz -i FixImg MovImg -gm MaskImg -it Affine_name -n 300x100 -e 0.5 -m NCC 3x3x2"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    run_command(job_string)  
    job_string = "greedy -d 3 -rf FixImg -rm MovImg MovImg_Warp1.nii.gz -r OutImg.nii.gz Affine_name"
    job_string = job_string.replace('Affine_name',Affine_name).replace('OutImg',output_name).replace('FixImg',template_name).replace('MovImg',Mov_name).replace('MaskImg',Mask_name)
    run_command(job_string)

#tif_file_folder='/faststorage/project/FUNCT_ENS/NewENSDataDK/20231204/041223_RS_4DPF_GF_F1_HINDGUT_range130_step5_exposure11_power60/'
tif_file_folder=sys.argv[1]
tif_file_folder=tif_file_folder.split('\r')[0]# removes the return to line
raw_string = r"{}".format(tif_file_folder)
tif_file_folder=os.path.normpath(tif_file_folder.split('3Dreg')[0])
print(tif_file_folder)

OutputFileAppendWarp=['Warp1','Warp2','Warp3']

img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[0]+'.nii.gz'))
if not img_seq_list:
 job_string=r'find '+tif_file_folder+r' -type f -name "*.nii" -exec gzip {} -f \;'
 run_command(job_string)
 img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*_orig.nii.gz'))

if len(img_seq_list)<EXPECTED_FRAME_COUNT :
  warp_1=False
  img_seq_list=glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif'))
  img_seq_list=[x for x in img_seq_list if 'Warped' not in x]
  img_seq_list=[x for x in img_seq_list if 'template' not in x]
else:
  warp_1=True

#You need to modify the next two lines to match where your template and masks are
template_name=os.path.join(tif_file_folder,'3Dreg/Newtemplate.tif')
mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
if not os.path.exists(mask_name):
 file_name=os.path.basename(img_seq_list[0])
 mask_name=file_name.split('_range')[0]+'_TEMPLATE.tif'
 date_name=mask_name.split('_RS_')[0]
 date_name='20'+date_name[-2:]+date_name[2:4]+date_name[0:2]
 mask_name=os.path.join(os.path.join(tif_file_folder),'RS_'+date_name+'_'+mask_name.split('_RS_')[1])

if not os.path.exists(template_name):
    temp_file=tifffile.imread(FindTemplate(tif_file_folder))
    tifffile.imwrite(template_name,temp_file.astype(np.uint16))

img_seq_list2=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[1]+'.nii.gz'))

if not img_seq_list:
    raise RuntimeError(
        "No input images found."
    )
print(img_seq_list[0])
print('number of files warped twice: '+str(len(img_seq_list2)))

#First check if the files were warped once, or twice
if len(img_seq_list)==EXPECTED_FRAME_COUNT  and len(img_seq_list2)<EXPECTED_FRAME_COUNT  and warp_1:
 print('need to do the second warp')
 for img_name in img_seq_list:
  if not os.path.exists(img_name.replace(OutputFileAppendWarp[0]+'.nii.gz',OutputFileAppendWarp[1]+'.nii.gz')):      
   Mov_name = img_name.replace(OutputFileAppendWarp[0]+'.nii.gz','')   
   Register_single_image_SecondPass(img_name,template_name,mask_name)
elif not warp_1:
 print('need to do the first and second warp')
 tif_list=[x for x in glob.glob(os.path.join(tif_file_folder,'3Dreg/*.tif')) if 'Warped' not in x]
 tif_list=[x for x in tif_list if 'template' not in x]
 for img_name in tif_list:
  Register_single_image(img_name,template_name,mask_name)
  Register_single_image_SecondPass(img_name.replace('.tif','.tif_Warp1.nii.gz'),template_name,mask_name)
else:
    print('Folder '+tif_file_folder+' has been warped twice')


#mask_name='/faststorage/project/FUNCT_ENS/TemplateFiles/Done/'+os.path.basename(tif_file_folder).split('_range')[0]+'_template.tif'
img_seq_list2=glob.glob(os.path.join(tif_file_folder,'3Dreg','*'+OutputFileAppendWarp[1]+'.nii.gz'))
print(os.path.join(tif_file_folder,'3Dreg/*_Warp2.nii.gz')+' '+str(len(img_seq_list2)))
if len(img_seq_list2)==EXPECTED_FRAME_COUNT:
 for img_name in img_seq_list2:
  Register_single_image_ThirdPass(img_name,template_name)
else:
    print('need to finish second warp')
    exit()

Warped_files=glob.glob(tif_file_folder+'/3Dreg/*'+os.path.basename(os.path.normpath(tif_file_folder))+'*_Warp3.nii.gz')    
#MC_img_list=[x for x in MC_img_list if not 'LongReg' in x]
print(tif_file_folder+' '+str(len(Warped_files)))
if not Warped_files:
    raise RuntimeError(
        "No Warp3 files found."
    )

if not os.path.isfile(Warped_files[0].replace('.nii.gz','.tif')):
    for file_Warp1 in Warped_files:
        base_img=nib.load(file_Warp1)
        base_img=np.squeeze(np.asarray(base_img.dataobj,dtype='uint16'))
        tifffile.imwrite(file_Warp1.replace('.nii.gz','.tif'),base_img,bigtiff=True)

print('finished processing') 
exit('done')