import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data

import os

cwd = os.getcwd()
test_rhd_data_path = os.path.join(cwd, 'src/tests/sampledata.rhd')

def test_read_rhd_data():
    intan_dict = read_rhd_data(test_rhd_data_path)

