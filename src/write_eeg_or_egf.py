from src.ephys_to_lfp import (
    intan_ephys_to_lfp_dict
    ,intan_to_lfp_header_dict
    ,down_sample_timeseries
    ,fir_hann
)

from src.filters import (
    iirfilt
    ,notch_filt
    ,get_a_b
)

import os
import struct
import numpy as np

__version__ = '1.0' # change this to a function for getting release version in future.




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

#-----------------------------------------------------------------------------------------------------------------------
def write_eeg_or_egf(EphysCollection, session_metadata, target_directory, session_name):
    data = EphysCollection.data
    assert len(EphysCollection.data) > 0, "EphysCollection is empty"
    for i, channel_name in enumerate(data.keys()):
        sample_rate = data[channel_name].sample_rate
        if sample_rate[0] <= 500:
            file_type = 'eeg'
        elif sample_rate[0] > 500:
            file_type = 'egf'


        if i > 0:
            n = str(i)
        else:
            n = ''
        path = os.path.join(target_directory, '{}.{}{}'.format(session_name, file_type, n))

        header = make_eeg_or_egf_header(EphysCollection.data[channel_name], session_metadata)

        with open(path, 'w') as f:
            for key, value in header.items():
                f.write('{} {}\n'.format(key, value))
            f.write('data_start')
        series = data[channel_name].data
        num_samples = len(series)
        if file_type == 'eeg':
            binary_data = struct.pack('>%db' % (
            ), *[np.int(data_value) for data_value in series.tolist()])
        elif file_type == 'egf':
            binary_data = struct.pack('<%dh' % (num_samples), *[int(data_value) for data_value in series.tolist()])
        with open(path, 'rb+') as f:
            f.seek(0, 2)
            f.write(binary_data)
            f.write(bytes('\r\ndata_end\r\n', 'utf-8'))



def make_eeg_or_egf_header(EphysSeries, session_metadata):
    """
    Make the header for the .eeg or .egf file.
    """

    voltage_series = EphysSeries.data
    sample_rate = EphysSeries.sample_rate

    if sample_rate[0] <= 500:
        #sample_rate is of the form (rate, 'Hz').
        file_type = 'eeg'
        bytes_per_sample = 1
        num_samples = len(voltage_series)
    elif sample_rate[0] > 500:
        file_type = 'egf'
        bytes_per_sample = 2
        num_samples = len(voltage_series)

    header = {}
    header['trial_date'] = session_metadata['trial_date']
    header['trial_time'] = session_metadata['trial_time']
    header['experimenter'] = session_metadata['experimenter']
    header['comments'] = session_metadata['comments']
    header['duration'] = len(voltage_series)*sample_rate[0]
    header['sw_version'] = 'neuroscikit version {}'.format(__version__)
    header['num_chans'] = '1'
    header['sample_rate'] = '{} {}'.format(sample_rate[0], sample_rate[1])
    header['bytes_per_sample'] = str(bytes_per_sample)
    header['num_{}_samples'.format(file_type.upper())] = str(len(voltage_series))

    return header


