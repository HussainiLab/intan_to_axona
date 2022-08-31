from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data
from src.filters import notch_filt, iirfilt, get_a_b

import os
import numpy as np
import scipy.signal
import struct
import datetime

def intan_to_lfp_dicts(intan_data: dict) -> dict:
    """
    Collects all the data needed for an egf file
    from the intan data and returns a dictionary
    ready for writing to an egf file for every channel.

    IMPORTANT NOTE: This function only collects
    electrophysiology data from the
    'amplifier_data' key. It does not collect
    signals from auxiliary inputs.
    """

    lfp_ephys_data = intan_ephys_to_lfp_dict(intan_data)

    lfp_header = intan_to_lfp_header_dict(intan_data)

    return lfp_ephys_data, lfp_header


def intan_ephys_to_lfp_dict(intan_data: dict, egf=True) -> dict:

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


def fir_hann(data, Fs, cutoff, n_taps=101, showresponse=0):

    # The Nyquist rate of the signal.
    nyq_rate = Fs / 2

    b = scipy.signal.firwin(n_taps, cutoff / nyq_rate, window='hann')

    a = 1.0
    # Use lfilter to filter x with the FIR filter.
    data = scipy.signal.lfilter(b, a, data)
    # data = scipy.signal.filtfilt(b, a, data)

    if showresponse == 1:
        w, h = scipy.signal.freqz(b, a, worN=8000)  # returns the requency response h, and the angular frequencies
        # w in radians/sec
        # w (radians/sec) * (1 cycle/2pi*radians) = Hz
        # f = w / (2 * np.pi)  # Hz

        plt.figure(figsize=(20, 15))
        plt.subplot(211)
        plt.semilogx((w / np.pi) * nyq_rate, np.abs(h), 'b')
        plt.xscale('log')
        plt.title('%s Filter Frequency Response')
        plt.xlabel('Frequency(Hz)')
        plt.ylabel('Gain [V/V]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(cutoff, color='green')

    return data, n_taps


def get_session_parameters(pos_file, rhd_file):

    session_parameters = {}
    intan_headers = read_data(rhd_file)
    if pos_file != None:
        with open(pos_file, 'rb+') as f:  # opening the .pos file
            for line in f:  # reads line by line to read the header of the file
                if 'comments' in str(line):
                    session_parameters['comments'] = line.decode(encoding='UTF-8')[len('comments '):-2]
                elif 'pixels_per_metre' in str(line):
                    session_parameters['ppm'] = float(line.decode(encoding='UTF-8')[len('pixels_per_metre '):-2])
                elif 'sw_version' in str(line):
                    session_parameters['version'] = line.decode(encoding='UTF-8')[len('sw_version '):-2]
                elif 'experimenter' in str(line):
                    session_parameters['experimenter'] = line.decode(encoding='UTF-8')[len('experimenter '):-2]
                elif 'min_x' in str(line) and 'window' not in str(line):
                    session_parameters['xmin'] = int(line.decode(encoding='UTF-8')[len('min_x '):-2])
                elif 'max_x' in str(line) and 'window' not in str(line):
                    session_parameters['xmax'] = int(line.decode(encoding='UTF-8')[len('max_x '):-2])
                elif 'min_y' in str(line) and 'window' not in str(line):
                    session_parameters['ymin'] = int(line.decode(encoding='UTF-8')[len('min_y '):-2])
                elif 'max_y' in str(line) and 'window' not in str(line):
                    session_parameters['ymax'] = int(line.decode(encoding='UTF-8')[len('max_y '):-2])

                elif 'window_min_x' in str(line):
                    session_parameters['window_xmin'] = int(line.decode(encoding='UTF-8')[len('window_min_x '):-2])

                elif 'window_max_x' in str(line):
                    session_parameters['window_xmax'] = int(line.decode(encoding='UTF-8')[len('window_max_x '):-2])

                elif 'window_min_y' in str(line):
                    session_parameters['window_ymin'] = int(line.decode(encoding='UTF-8')[len('window_min_y '):-2])

                elif 'window_max_y' in str(line):
                    session_parameters['window_ymax'] = int(line.decode(encoding='UTF-8')[len('window_max_y '):-2])

                elif 'duration' in str(line):
                    session_parameters['duration'] = int(line.decode(encoding='UTF-8')[len('duration '):-2])

                if 'data_start' in str(line):
                    break

        # ----------------
        n_channels = len(intan_headers['amplifier_channels'])
        notch_filter_setting = intan_headers['frequency_parameters']['notch_filter_frequency']

        ADC_Fullscale = 1500

        session_parameters['gain'] = np.zeros(n_channels)
        session_parameters['fullscale'] = ADC_Fullscale
        session_parameters['n_channels'] = n_channels
        session_parameters['notch_frequency'] = notch_filter_setting
        session_parameters['pretrigSamps'] = 10
        session_parameters['spikeLockout'] = 40
        session_parameters['rejthreshtail'] = 43
        session_parameters['rejstart'] = 30
        session_parameters['rejthreshupper'] = 100
        session_parameters['rejthreshlower'] = -100
        session_parameters['Fs'] = 48e3

    return session_parameters



def intan_to_lfp_header(intan_data: dict, egf=True) -> dict:
    lfp_header = dict()
    lfp_header['date'] = 'UNKNOWN'
    lfp_header['time'] = 'UNKNOWN'
    lfp_header['experimenter'] = 'UNKNOWN'
    lfp_header['comments'] = 'UNKNOWN'
    lfp_header['duration'] = 'UNKNOWN'
    lfp_header['version'] = 'UNKNOWN'
    if egf:
        lfp_header['sample_rate'] = 4.8e3
    else: #(if eeg)
        lfp_header['sample_rate'] = 250.0 #TODO: Check this

    for key in intan_data['frequency_parameters'].keys():
        lfp_header[key] = intan_data['frequency_parameters'][key]
    lfp_header['channels'] = [intan_data['amplifier_channels'][i]['native_channel_name'] for i in range(len(intan_data['amplifier_channels']))]

    return lfp_header

def get_set_header(set_filename):
    with open(set_filename, 'r+') as f:
        header = ''
        for line in f:
            header += line
            if 'sw_version' in line:
                break
    return header

def intan_scalar():
    """returns the scalar value that can be element-wise multiplied to the data
    to convert from bits to micro-volts"""
    Vswing = 2.45
    bit_range = 2 ** 16  # it's 16 bit system
    gain = 192  # V/V, listed in the intan chip's datasheet
    return (1e6) * (Vswing) / (bit_range * gain)




