import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.data_voltage import (
    EphysSeries
    ,EphysCollection
)

from src.write_eeg_or_egf import (
    write_eeg_or_egf
    ,make_eeg_or_egf_header
)



from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data

import numpy as np

raw_series = np.random.normal(size=1000)
data_dict = {'ephys_series': raw_series, 'units': 'mV', 'sample_rate': (1000, 'Hz')}

series = EphysSeries(data_dict)
channel_dict = {'channel_1': series}
collection = EphysCollection(channel_dict)

session_metadata = {
    'trial_date': '2019-01-01'
    ,'trial_time': '12:00:00'
    ,'experimenter': 'John Doe'
    ,'comments': 'This is a test'
    }

intan_data = read_rhd_data(PROJECT_PATH + '/src/tests/sampledata.rhd')

def test_make_eeg_or_egf_header():
    """
    This module is for local field potential (LFP) data. These data are measured
    """
    header = make_eeg_or_egf_header(series, session_metadata)
    print(header)


def test_write_eeg_or_egf():
    """
    This module is for local field potential (LFP) data. These data are measured
    """
    write_eeg_or_egf(collection, session_metadata, './test_outputs', 'test')

def test_create_eeg_and_egf_files():
    create_eeg_and_egf_files(intan_data, 'test', PROJECT_PATH + '/test_outputs')

