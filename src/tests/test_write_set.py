import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.write_set import (
    write_set
    ,get_session_parameters
    ,default_set_dict
)
test_dir = os.path.join(PROJECT_PATH, 'src/tests')
output_file_path = os.path.join(test_dir, 'test.set')


def test_get_session_parameters():
    session_parameters = get_session_parameters(n_channels=4, default_set_dict = default_set_dict())
    counter = 0
    for value in session_parameters.values():
        if value == None:
            counter += 1
    print('{} keys not defined'.format(counter))

def test_write_set():
    session_parameters = get_session_parameters(n_channels=4, default_set_dict = default_set_dict())
    print(session_parameters['a_in_ch_1'])
    write_set(session_parameters, output_file_path)