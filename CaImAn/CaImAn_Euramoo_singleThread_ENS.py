import sys
import os
import numpy as np
from scipy.io import savemat
import caiman as cm
from caiman.motion_correction import MotionCorrect
from caiman.components_evaluation import evaluate_components
import caiman.source_extraction.cnmf as cnmf
import tifffile
fnames=[sys.argv[1]]	#name of the movie
fnames_orig=fnames
final_frate=int(os.environ["FPS"]) # frame rate in Hz
K=int(os.environ["COMP"]) # number of neurons expected per patch, that seems to work well
#K=None
n_processes = 5 # if using the intel nodes
single_thread=True   
dview=None
gSig=[5,5] # expected half size of neurons, works for nuclear GCaMP
merge_thresh=0.8 # merging threshold, max correlation allowed
p=1 #order of the autoregressive system
downsample_factor=1 # use .2 or .1 if file is large and you want a quick answers
final_frate=final_frate*downsample_factor
init_method='greedy_roi'
spatial_factor=1
idx_xy=None
base_name=os.environ["TMPDIR"]+"/"+fnames[0].split('/')[-1][:-4]
print(fnames)
min_mov = cm.load(fnames[0], subindices=(0,10,10)).min()
mc = MotionCorrect(fnames[0],min_mov,max_shifts = [5,5],dview=dview,splits_rig = 1)    
mc.motion_correct_rigid(save_movie=True)
border_to_0 = np.ceil(np.max(mc.shifts_rig)).astype(np.int)
base_name=os.environ["TMPDIR"]+"/"+mc.fname_tot_rig.split('/')[-1][:-4]
fname_new = cm.save_memmap([mc.fname_tot_rig], base_name=base_name+'b', border_to_0=border_to_0)
Yr,dims,T=cm.load_memmap(fname_new)
Y=np.reshape(Yr,dims+(T,),order='F')
tifffile.imsave(fnames[0][:-4]+'_mean.tiff',np.mean(Y,axis=2))
nb_back=2
options = cnmf.utilities.CNMFSetParms(Y,n_processes,p=p,gSig=gSig,K=K,ssub=1,tsub=1,nb=nb_back,n_pixels_per_process=1000,block_size=1000, remove_very_bad_comps=True)
Cn = cm.local_correlations(Y)
Yr,sn,g,psx = cnmf.pre_processing.preprocess_data(Yr,dview=dview,n_pixels_per_process=1000, noise_range = [0.25,0.5],noise_method = 'logmexp', compute_g=False,  p = 1,lags = 5, include_noise = False, pixels = None,max_num_samples_fft=3000, check_nan = True)
options['init_params']['use_hals']=True
Ain,Cin, b_in, f_in, center=cnmf.initialization.initialize_components(Y, **options['init_params'])
Ain,b_in,Cin, f_in = cnmf.spatial.update_spatial_components(Yr, Cin, f_in, Ain, sn=sn, dview=dview,**options['spatial_params'])
options['temporal_params']['n_pixels_per_process']=1000
options['spatial_params']['block_size']=1000
if Cin.size > 0:
	options['temporal_params']['p'] = 0 # set this to zero for fast updating without deconvolution
	Cin,Ain,b_in,f_in,S,bl,c1,neurons_sn,g,YrA,lam = cnmf.temporal.update_temporal_components(Yr,Ain,b_in,Cin,f_in,bl=None,c1=None,sn=None,g=None,**options['temporal_params'])		
	Ain,Cin,nr_m,merged_ROIs,S_m,bl_m,c1_m,sn_m,g_m=cnmf.merging.merge_components(Yr,Ain,b_in,Cin,f_in,S,sn,options['temporal_params'], options['spatial_params'],dview=dview, bl=bl, c1=c1, sn=neurons_sn, g=g, thr=merge_thresh,mx=1000, fast_merge = True)	
	Ain,b_in,Cin, f_in = cnmf.spatial.update_spatial_components(Yr, Cin, f_in, Ain, sn=sn, dview=dview,**options['spatial_params'])	
	options['temporal_params']['p'] = p # set it back to original value to perform full deconvolution	
	Cin,Ain,b_in,f_in,S,bl,c1,neurons_sn,g,YrA,lam = cnmf.temporal.update_temporal_components(Yr,Ain,b_in,Cin,f_in,bl=None,c1=None,sn=None,g=None,**options['temporal_params'])		
	traces=Cin+YrA
	tB = np.minimum(-2,np.floor(-5./30*final_frate))
	tA = np.maximum(5,np.ceil(25./30*final_frate))
	fitness_raw, fitness_delta, erfc_raw,erfc_delta,r_values,num_significant_samples = evaluate_components(Y,traces,Ain,Cin,bl,f_in, final_frate, remove_baseline = True, N = 5, robust_std = False, Athresh = 0.1, Npeaks = 5, thresh_C = 0.2)	
    
	idx_components_r=np.where(r_values>=.6)[0]
	idx_components_raw=np.where(fitness_raw<-40)[0]        
	idx_components_delta=np.where(fitness_delta<-20)[0]
	idx_components=np.union1d(idx_components_r,idx_components_raw)
	idx_components=np.union1d(idx_components,idx_components_delta)  	
	idx_components_bad=np.setdiff1d(range(len(traces)),idx_components)	
	savemat(fnames_orig[0][:-4]+'_output_analysis_matlab.mat',mdict={'ROIs':Ain,'DenoisedTraces':Cin,'Baseline':bl, 'Noise':YrA, 'Spikes': S,'idx_components':idx_components})
	savemat(fnames_orig[0][:-4]+'_output_correlation.mat',mdict={'Correlation_image':Cn})

