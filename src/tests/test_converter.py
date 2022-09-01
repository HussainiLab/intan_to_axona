import os
import sys
PROJECT_PATH = os.getcwd()
sys.path.append(PROJECT_PATH)

from src.converter import convert_all_files

test_dir = PROJECT_PATH + r'\src\tests'

output_path = PROJECT_PATH + r'\test_outputs'

rhd_path = test_dir + r'\sampledata.rhd'

pos_json_path = test_dir + r'\pos_header.json'

pos_csv_path = test_dir + r'\Book1.csv'

pos_txt_path = None

def test_convert_all_files():
    convert_all_files(output_path, rhd_path, None, None)
    convert_all_files(output_path, rhd_path, pos_csv_path, pos_json_path)
