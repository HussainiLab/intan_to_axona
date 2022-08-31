

def ephys_to_lfp_header_dict(intan_data: dict, egf=True) -> dict:
    lfp_header = dict()
    lfp_header['date'] = None
    lfp_header['time'] = None
    lfp_header['experimenter'] = None
    lfp_header['comments'] = None
    lfp_header['duration'] = None
    lfp_header['version'] = None
    if egf:
        lfp_header['sample_rate'] = 4.8e3
    else: #(if eeg)
        lfp_header['sample_rate'] = 250.0 #TODO: Check this

    for key in intan_data['frequency_parameters'].keys():
        lfp_header[key] = intan_data['frequency_parameters'][key]
    lfp_header['channels'] = [intan_data['amplifier_channels'][i]['native_channel_name'] for i in range(len(intan_data['amplifier_channels']))]

    return lfp_header