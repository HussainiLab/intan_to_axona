
def intan_to_eeg_and_egf(intan_file_path: str, session_name: str, output_dir: str):
    """
    """
    intan_data = read_rhd_data(intan_file_path)
    intan_sample_rate = intan_data['frequency_parameters']['amplifier_sample_rate']
    lfp_ephys_data = intan_ephys_to_lfp_dict(intan_data)
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
            eeg_ephys_data = down_sample_timeseries(filtered_data, 4.8e3, 250)

            eeg_ephys_data = eeg_ephys_data.astype(np.int8)


            write_eeg_or_egf_file(eeg_ephys_data, duration, eeg_header, channel, session_name, output_dir, is_egf=False)