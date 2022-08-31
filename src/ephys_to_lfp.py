from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data
from src.filters import notch_filt, iirfilt, get_a_b, fir_hann

import os
import numpy as np
import scipy.signal
import struct
import datetime


def ephys_to_lfp_dict(intan_data: dict, egf=True) -> dict:

    amplifier_sample_rate = float(intan_data['frequency_parameters']['amplifier_sample_rate'])

    if egf:
        sample_rate = 4.8e3
    else:
        sample_rate = 250.0

    try:
        assert len(intan_data['amplifier_data']) == len(intan_data['amplifier_channels'])
    except AssertionError:
        raise ValueError('The number of amplifier channels does not match the number of custom channel names. This file may be corrupted.')

    lfp_ephys_data = dict()
    lfp_ephys_data['time'] = down_sample_timeseries(intan_data['t_amplifier'].flatten(), amplifier_sample_rate, sample_rate)
    for i in range(len(intan_data['amplifier_data'])):
        if intan_data['amplifier_data'][i].size > 1:
            lfp_ephys_data[intan_data["amplifier_channels"][i]["native_channel_name"]] = down_sample_timeseries(intan_data['amplifier_data'][i], amplifier_sample_rate, sample_rate)

    return lfp_ephys_data


def down_sample_timeseries(data: np.ndarray, sample_rate: float, new_sample_rate: float):
    """
    Downsample a timeseries.
    """
    try:
        assert type(data) == np.ndarray
    except:
        raise TypeError('data must be a numpy array')
    try:
        assert data.ndim == 1
    except:
        raise ValueError('data must be a 1D array')
    try:
        assert type(float(sample_rate)) == float
    except:
        raise TypeError('sample_rate must be a number')
    try:
        assert type(float(new_sample_rate)) == float
    except:
        raise TypeError('new_sample_rate must be a float')
    try:
        assert sample_rate > new_sample_rate
    except:
        raise ValueError('sample_rate must be greater than new_sample_rate')

    #Generate a
    skip_size = sample_rate / new_sample_rate

    #is this necessary?
    data = data.flatten()

    #Generate a list of floating points where the new
    # data would ideally be sampled from.
    subsample = np.arange(0, data.size, skip_size)
    #Find the nearest index value to the subsample.
    new_index = [int(round(i)) for i in subsample]

    if len(data) == new_index[-1]:
        new_index.pop()

    #Downsample the data.
    downsampled_data = data[new_index]

    # clip the data to the lower bound of
    # the expected size
    end = int(round(len(data) / (sample_rate / new_sample_rate) - 1))

    if len(downsampled_data) >= end:
        downsampled_data = downsampled_data[:end]
    else:
        raise ValueError('The data is not long enough to downsample.')


    return downsampled_data




def intan_scalar():
    """returns the scalar value that can be element-wise multiplied to the data
    to convert from bits to micro-volts"""
    Vswing = 2.45
    bit_range = 2 ** 16  # it's 16 bit system
    gain = 192  # V/V, listed in the intan chip's datasheet
    return (1e6) * (Vswing) / (bit_range * gain)




