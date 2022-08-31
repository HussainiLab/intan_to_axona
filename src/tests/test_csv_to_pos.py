from asyncore import write
import numpy as np
import pandas as pd
import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)


output_path = PROJECT_PATH + r'\\test_outputs'
# output_path = r'C:\Users\aaoun\OneDrive - cumc.columbia.edu\Desktop\HussainiLab\intan_to_axona\src\tests\test.pos'
csv_path = PROJECT_PATH + r'\src\tests\Book1.csv'


from src.csv_to_pos import (
    pd_to_dict,
    write_pos,
)


def test_pd_to_dict():
    data_frame = pd.read_csv(csv_path)

    pos_dict = pd_to_dict(data_frame=data_frame)

    assert type(pos_dict) == dict
    assert type(pos_dict['t']) == list

def test_text_to_dict():
    pass

def test_write_pos():
    data_frame = pd.read_csv(csv_path)

    pos_dict = pd_to_dict(data_frame=data_frame)
    print(pos_dict)
    fpath = output_path + '/write_pos_test.pos'

    write_pos(fpath, pos_dict)

if __name__ == '__main__':
    test_pd_to_dict()
    # test_text_to_dict()
    test_write_pos()
    print('we good')
