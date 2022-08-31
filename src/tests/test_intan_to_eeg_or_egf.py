import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.intan_to_eeg_and_egf import (
    intan_to_eeg_and_egf
    ,write_eeg_or_egf_file
)

intan_path = PROJECT_PATH + '/src/tests/sampledata.rhd'
session_name = 'test'
output_dir = PROJECT_PATH + '/test_outputs'

def test_intan_to_eeg_and_egf():
    intan_to_eeg_and_egf(intan_path, session_name, output_dir)