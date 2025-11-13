# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 15:47:00 2025

@author: au691573
"""

import pandas as pd
import numpy as np
import json
import mne
import os
import glob
import kedm
import sys


def load_data_tsv(filename):
    data = pd.read_csv(filename, sep='\t', compression='gzip', header=None)
    signal = data.values  
    metadata_filename = filename.replace('.tsv.gz', '.json')
    with open(metadata_filename, 'r') as file:
        metadata = json.load(file)
    return signal, metadata['Columns']

def load_metadata(metadata_filename):
    with open(metadata_filename, 'r') as file:
        metadata = json.load(file)
    return metadata
def load_physio(signal_file, rate_file, peak_file):
    signal_df = pd.read_csv(signal_file, sep='\t', compression='gzip', header=None)
    rate_df = pd.read_csv(rate_file, sep='\t', compression='gzip')
    peak_df = pd.read_csv(peak_file, sep='\t', compression='gzip')
    signal = signal_df.values  
    rate = rate_df[1:].values
    peaks_time = peak_df[1:].values    
    return signal, rate, peaks_time

def load_signals(filename):
    data = pd.read_csv(filename, sep='\t', compression='gzip', header=None)
    return data.values  

def load_columns(filename):
    metadata_filename = filename.replace('.tsv.gz', '.json')
    with open(metadata_filename, 'r') as file:
            metadata = json.load(file)
    return metadata['Columns']


download_dir='/faststorage/project/Student_ENS/BrainBody/'
result_dir=download_dir
download_dir=str(sys.argv[1])
base_dir=os.path.dirname(os.path.normpath(download_dir))
exp_list=[download_dir.split('experiment')[1].split(os.sep)[0]]
#exp_list= [4,5]
#exp_list.sort()
print(exp_list)

for exp_no in exp_list:    
    #base_dir = os.path.join(base_dir, 'experiment'+str(exp_list[0]))
    print(base_dir)
    #sub_list = [x.split('sub-')[1].split(os.sep)[0] for x in glob.glob(os.path.join(base_dir,'sub-*/'))]
    #sub_list.sort()
    #for sub in sub_list:
    sub=download_dir.split('sub-')[1].split(os.sep)[0]
    ses_list = [x.split('ses-')[1].split(os.sep)[0] for x in glob.glob(os.path.join(download_dir,'ses-*/'))]
    print(sub)
    print(ses_list)
    for ses in ses_list:    
        if not os.path.exists(os.path.join(base_dir,'sub-'+str(sub),'ses-'+str(ses),'eeg')):
            print('No Data in '+os.path.join(base_dir,'sub-'+str(sub),'ses-'+str(ses),'eeg'))
            continue
        else:
            stim_list = [x.split('stim')[1].split('_')[0] for x in glob.glob(os.path.join(base_dir,'sub-'+str(sub),'ses-'+str(ses),'eeg','*-stim*.bdf'))]
            if not stim_list:
                continue
            else:
                for stim in stim_list:
                    if os.path.exists(os.path.join(download_dir,'results','experiment'+str(exp_no)+rf'sub-{sub}_ses-{ses}_task-stim{stim}_ccm_rho_Brainbody.npy')):
                        continue
                    else:                            
                        particpants_filename = os.path.join(base_dir, 'participants.tsv')
                        particpants = pd.read_csv(particpants_filename, sep='\t')
                        
                        #### Raw Data Files ####
                        
                        eeg_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','eeg',rf'sub-{sub}_ses-{ses}_task-stim{stim}_eeg.bdf') #eeg subdirectory
                        eeg_metadata_filename = eeg_filename.replace('.bdf', '.json') #eeg subdirectory
                        
                        ecg_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_recording-ecg_physio.tsv.gz') 
                        ecg_metadata_filename = ecg_filename.replace('.tsv.gz', '.json') 
                        
                        resp_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_recording-respiration_physio.tsv.gz') 
                        resp_metadata_filename = resp_filename.replace('.tsv.gz', '.json') 
                        
                        eog_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_recording-eog_physio.tsv.gz')
                        eog_metadata_filename = eog_filename.replace('.tsv.gz', '.json') 
                        
                        gaze_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_gaze_visualangle_eyetrack.tsv.gz')  
                        gaze_metadata_filename = gaze_filename.replace('.tsv.gz', '.json') 
                        
                        pupil_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_pupil_eyetrack.tsv.gz')  
                        pupil_metadata_filename = pupil_filename.replace('.tsv.gz', '.json') 
                        
                        #head_filename = os.path.join(base_dir, rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_head_eyetrack.tsv.gz')  
                        #head_metadata_filename = head_filename.replace('.tsv.gz', '.json') 
                        
                        #### Derived Data Files ####
                        
                        # Pre-processed EEG data
                        derived_eeg_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eeg',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-eeg.bdf')
                        
                        # Pre-processed ECG data
                        derived_ecg_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-filteredECG.tsv.gz')
                        
                        # Pre-processed eyetracking data
                        #derived_pupil_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-pupil_eyetrack.tsv.gz')
                        #derived_gaze_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-gaze_visualangle_eyetrack.tsv.gz')
                        #derived_head_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-head_eyetrack.tsv.gz')
                        
                        # Interpolation mask of pupil and gaze data that are interpolated [1 = interpolated sample, 0 = normal sample]
                        #pupil_interpolated_idx_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-pupil_interpolated_idx_mask_eyetrack.tsv.gz')
                        #gaze_interpolated_idx_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-gaze_interpolated_idx_mask_eyetrack.tsv.gz')
                        
                        # Rates
                        hr_file_name = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-heartrate.tsv.gz')
                        rr_file_name = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-breathrate.tsv.gz')
                        #sr_file_name = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-saccaderate.tsv.gz')
                        #br_file_name = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-blinkrate.tsv.gz')
                        #fr_file_name = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-fixationrate.tsv.gz')
                        
                        # Discrete events' timestamps of occurances
                        rpeak_timestamps_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-rpeak_timestamps.tsv.gz')
                        breath_peak_timestamps_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','beh',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-breath_peak_timestamps.tsv.gz')
                        #saccade_timestamps_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-saccades.tsv.gz')
                        #blink_timestamps_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-blinks.tsv.gz')
                        #fixation_timestamps_filename = os.path.join(base_dir, rf'derivatives',rf'sub-{sub}',rf'ses-{ses}','eyetrack',rf'sub-{sub}_ses-{ses}_task-stim{stim}_desc-fixations.tsv.gz')
                        
                        
                        # mne
                        mne.set_log_level("WARNING") 
                        raw = mne.io.read_raw_bdf(eeg_filename, preload=True)
                        eeg_signal = raw.get_data()
                        print("mne - EEG Signals Shape: ", eeg_signal.shape)
                                                                    
                        ecg, ecg_columns = load_data_tsv(ecg_filename)
                        ecg_metadata = load_metadata(ecg_metadata_filename)                        
                        #head, head_columns = load_data_tsv(head_filename)                        
                        #head_metadata = load_metadata(head_metadata_filename)
                        #gaze, gaze_columns = load_data_tsv(gaze_filename)
                        #gaze_metadata = load_metadata(gaze_metadata_filename)                        
                        fs = 128  # Sampling rate (Hz)
                        
                        
                        # Filenames and labels (raw vs. derived)
                        raw_filenames = [ecg_filename, resp_filename]
                        #raw_filenames = [
                        #    ecg_filename, gaze_filename, head_filename, pupil_filename, 
                        #    resp_filename, eog_filename
                        #]
                        raw_labels = [load_columns(ecg_filename),load_columns(resp_filename)]
                        #    load_columns(ecg_filename), load_columns(gaze_filename), load_columns(head_filename), load_columns(pupil_filename), 
                        #    load_columns(resp_filename), load_columns(eog_filename)
                        #]
                        
                        derived_filenames = [derived_ecg_filename,rr_file_name,hr_file_name]
                            #derived_ecg_filename, derived_gaze_filename, derived_head_filename, derived_pupil_filename,
                            #rr_file_name, hr_file_name, 
                            #br_file_name, sr_file_name, fr_file_name 
                        #]
                        derived_labels = [['Processed ECG'],['Breath Rate'], ['Heart Rate']]
                        #    ['Processed ECG'], load_columns(gaze_filename), load_columns(head_filename), load_columns(pupil_filename), 
                        #    ['Breath Rate'], ['Heart Rate'], 
                        #    ['Blink Rate'], ['Saccade Rate'], ['Fixation Rate']
                        #]
                        
                        # Load raw signals
                        raw_data = [load_signals(f) for f in raw_filenames]
                        # Add raw EEG to the beginning of this list
                        raw_eeg = mne.io.read_raw_bdf(eeg_filename).get_data()
                        raw_data.insert(0, np.mean(raw_eeg, axis=0)) # Add mean EEG
                        raw_labels.insert(0, ['Mean Avg EEG'])
                        
                        # Load processed signals
                        derived_data = [load_signals(f) for f in derived_filenames]
                        # Add processed EEG to the beginning of this list
                        derived_eeg = mne.io.read_raw_bdf(derived_eeg_filename).get_data()
                        derived_data.insert(0, np.mean(derived_eeg, axis=0)) # Add mean EEG
                        derived_labels.insert(0, ['Mean Avg EEG'])
                        
                        breath_signal, breath_rate,breath_peaks=load_physio(resp_filename, rr_file_name, breath_peak_timestamps_filename)
                        heart_signal, heart_rate,heart_peaks=load_physio(derived_ecg_filename, hr_file_name, rpeak_timestamps_filename)
                        
                        length_timeserie=min([max(derived_eeg.shape), max(derived_data[1].shape),max(heart_rate.shape),max(breath_signal.shape),max(breath_rate.shape)])
                                
                        timeseries=np.column_stack((derived_eeg[:,0:length_timeserie].transpose(),derived_data[1][0:length_timeserie],heart_rate[0:length_timeserie],breath_signal[0:length_timeserie],breath_rate[0:length_timeserie]))
                        print(timeseries.shape)
                        #Embed_dims=[None] * timeseries.shape[1]
                        #for i in range(0,timeseries.shape[1]):
                        #    Embed_dims[i]=kedm.edim(timeseries[:,i],30,5,1)
                        #    
                        #np.save(os.path.join(result_dir,'results','experiment'+str(exp_no)+rf'sub-{sub}_ses-{ses}_task-stim{stim}_Embed_dims.npy'),Embed_dims)
                        Embed_dims=np.load(os.path.join(result_dir,'results','experiment'+str(exp_no)+rf'sub-{sub}_ses-{ses}_task-stim{stim}_Embed_dims.npy'))
                        ccm_rho=kedm.xmap(timeseries,Embed_dims,5,20)
                        np.save(os.path.join(result_dir,'results','experiment'+str(exp_no)+rf'sub-{sub}_ses-{ses}_task-stim{stim}_xmapDelay20.npy'),ccm_rho)              
                        