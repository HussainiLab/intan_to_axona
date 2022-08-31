import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.load_intan_rhd_format.load_intan_rhd_format import read_rhd_data
from src.read_rhd import read_rhd

import os

cwd = os.getcwd()
test_rhd_data_path = os.path.join(cwd, 'src/tests/sampledata.rhd')

def test_read_rhd_data():
    rhd_data = read_rhd_data(test_rhd_data_path)

def test_read_rhd():
    pass

