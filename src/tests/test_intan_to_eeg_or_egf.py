import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.intan_to_eeg_and_egf import (
    intan_to_eeg_and_egf
    ,write_eeg_or_egf_file
)


def test_write_eeg_or_egf_file():
    write_eeg_or_egf_file()