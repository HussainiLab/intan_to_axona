from src.ephys_to_lfp import ephys_to_lfp_dict, down_sample_timeseries
from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data
from src.filters import iirfilt, notch_filt, get_a_b, fir_hann

import struct

import numpy as np
import os


def intan_to_eeg_and_egf(intan_file_path: str, session_name: str, output_dir: str):
    """
    """
    intan_data = read_rhd_data(intan_file_path)
    intan_sample_rate = intan_data['frequency_parameters']['amplifier_sample_rate']
    lfp_ephys_data = ephys_to_lfp_dict(intan_data)
    time = lfp_ephys_data['time']
    duration = time[-1] - time[0]

    efg_header = intan_to_lfp_header_dict(intan_data, True)

    eeg_header = intan_to_lfp_header_dict(intan_data, False)

    for channel in lfp_ephys_data:
        if channel == 'time':
            continue
        else:
            irfiltered_data = iirfilt(bandtype='low', data=lfp_ephys_data[channel], Fs=intan_sample_rate, Wp=500, order=6,automatic=0, Rp=0.1, As=60, filttype='cheby1', showresponse=0)

            filtered_data = notch_filt(irfiltered_data, Fs=intan_sample_rate, freq=60, band=10,order=2, showresponse=0)

            # EGF
            egf_ephys_data = down_sample_timeseries(filtered_data, intan_sample_rate, 4.8e3)

            # converting the data from uV to int16
            #egf_ephys_data = (egf_ephys_data / scalar16)

            # ensuring the appropriate range of the values
            #egf_ephys_data[np.where(egf_ephys_data > 32767)] = 32767
            #egf_ephys_data[np.where(egf_ephys_data < -32768)] = -32768

            egf_ephys_data = egf_ephys_data.astype(np.int16)


            write_eeg_or_egf_file(egf_ephys_data, duration, efg_header, channel, session_name, output_dir, is_egf=True)


            # EEG
            eeg_ephys_data, N = fir_hann(egf_ephys_data, 4.8e3, 125, n_taps=101, showresponse=0)

            # converting data from int16 to int8
            #value = np.divide(eeg_ephys_data, 256).astype(int)
            #eeg_ephys_data[np.where(eeg_ephys_data > 127)] = 127
            #eeg_ephys_data[np.where(eeg_ephys_data < -128)] = -128

            # downsample the data
            eeg_ephys_data = down_sample_timeseries(eeg_ephys_data, 4.8e3, 250)

            eeg_ephys_data = eeg_ephys_data.astype(np.int8)


            write_eeg_or_egf_file(eeg_ephys_data, duration, eeg_header, channel, session_name, output_dir, is_egf=False)


def write_eeg_or_egf_file(lfp_single_unit_data, duration,lfp_header_dict, channel_name, session_name, output_dir, is_egf=False):
    """Writes a single channel of eeg data to a .eeg file.

    Parameters
        lfp_single_unit_data : numpy.array
            The data to be written to the .eeg file.
        duration : float
            The duration of the data in seconds.
        eeg_header_dict : dict
            The header dictionary for the .eeg file.
        channel_name : str
            The name of the channel to be written to the .eeg file.
        session_name : str
            The name of the session to be written to the .eeg file.
        output_dir : str
            The output directory for the .eeg file.

    Returns
        None
            (Writes a .eeg file to the output directory without returning an output.)
    """

    if is_egf:
        filepath = os.path.join(output_dir, "for_hfoGUI_" + session_name + '.egf{}'.format(channel_name[-3:]))
    else:
        filepath = os.path.join(output_dir, session_name + '.eeg{}'.format(channel_name[-3:]))


    with open(filepath, 'w') as f:
        header = "\nThis data set was created by the hfoGUI software."

        num_chans = '\nnum_chans 1'

        num_samples = len(lfp_single_unit_data)

        if is_egf:
            sample_rate = '\nsample_rate 4.8e3'
            b_p_sample = '\nbytes_per_sample 2'
        else:
            sample_rate = '\nsample_rate 250 Hz'
            b_p_sample = '\nbytes_per_sample 1'

        num_samples_line = '\nnum_samples %d' % (num_samples)

        p_position = '\nsamples_per_position %d' % (5)

        duration = '\nduration %.3f' % (duration)

        start = '\ndata_start'

        write_order = [header, num_chans,sample_rate, p_position, b_p_sample, num_samples_line, start]

        # write the header to the file
        f.writelines(write_order)

    # write the data to the file
    if is_egf:
        data = struct.pack('<%dh' % (num_samples), *[np.int16(data_value) for data_value in lfp_single_unit_data.tolist()])
    else:
        data = struct.pack('<%dh' % (num_samples), *[np.int8(data_value) for data_value in lfp_single_unit_data.tolist()])


    with open(filepath, 'rb+') as f:
        f.seek(0, 2)
        f.writelines([data, bytes('\r\ndata_end\r\n', 'utf-8')])

def intan_to_lfp_header_dict(intan_data: dict, egf=True) -> dict:
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