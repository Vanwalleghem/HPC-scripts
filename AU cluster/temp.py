# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 09:09:45 2025

@author: au691573
"""

from kilosort import io
import numpy as np
import os
import h5py
#import matplotlib.pyplot as plt
from spikeinterface.extractors import read_maxwell
#import pandas as pd

folder='/faststorage/project/CONNECT_ENS/Lilian/20250816'

data_folder=os.path.normpath(folder)
file_name=r'Network data.raw.h5'
data_file=os.path.join(data_folder,file_name)
h5_file=h5py.File(data_file)
recording_list=list(h5_file['recordings'].keys())
well_list=list(h5_file['wells'].keys())
nb=0
well_id=well_list[nb]
se_data=read_maxwell(data_file,stream_id=well_id)
se_data

# NOTE: Data will be saved as np.int16 by default since that is the standard
#       for ephys data. If you need a different data type for whatever reason
#       such as `np.uint16`, be sure to update this.
dtype = np.int16
filename, N, c, s, fs, probe_path = io.spikeinterface_to_binary(
    se_data, data_folder, data_name='data.bin', dtype=dtype,export_probe=True, probe_name='probe.prb'
    )

from kilosort import run_kilosort

# NOTE: 'n_chan_bin' is a required setting, and should reflect the total number
#       of channels in the binary file, while probe['n_chans'] should reflect
#       the number of channels that contain ephys data. In many cases these will
#       be the same, but not always. For example, neuropixels data often contains
#       385 channels, where 384 channels are for ephys traces and 1 channel is
#       for some other variable. In that case, you would specify
#       'n_chan_bin': 385.

# Specify probe configuration.
assert probe_path is not None, 'No probe information exported by SpikeInterface'
probe = io.load_probe(probe_path)

x_pos=np.asarray(list(set(probe['xc'])))
x_pos.sort()
dminx=np.median(np.diff(x_pos))
Th_universal = 8
x_centers = 30
nt = int(1 + 2*fs/1000) #2ms +1 for the value

settings = {'fs': fs, 'n_chan_bin': c,'Th_universal' : Th_universal, 'nt':nt,'dminx':dminx,'x_centers':x_centers}

# This command will both run the spike-sorting analysis and save the results to
# `DATA_DIRECTORY`.
ops, st, clu, tF, Wall, similar_templates, is_ref, \
    est_contam_rate, kept_spikes = run_kilosort(
        settings=settings, probe=probe, filename=filename)