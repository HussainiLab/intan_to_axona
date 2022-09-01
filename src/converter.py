from src.intan_to_eeg_and_egf import intan_to_eeg_and_egf
from csv_to_pos import write_pos, pd_to_dict, text_to_dict

def convert_all_files(target_directory, rhd_file_path, txt_or_csv_path=None):

    assert os.path.exists(rhd_file_path), "The path to the .rhd file does not exist."
    assert os.path.exists(target_directory), "The path to the output directory does not exist."
    assert txt_or_csv_path is None or os.path.exists(txt_or_csv_path), "The path to the .txt or .csv file does not exist."

    session_name = get_session_name_from_rhd_file_path(rhd_file_path)

    intan_to_eeg_and_egf(rhd_file_path, session_name, target_directory)

    if txt_or_csv_path is not None:
        if txt_or_csv_path.endswith('.txt'):
            pos_dict = text_to_dict(txt_or_csv_path)
        elif txt_or_csv_path.endswith('.csv'):
            pos_dict = pd_to_dict(txt_or_csv_path)
        else:
            raise ValueError("The path to the .txt or .csv file is not valid.")

        pos_write_path = os.path.join(target_directory, session_name + '.pos')

        write_pos(pos_write_path, pos_dict)

def get_session_name_from_rhd_file_path(rhd_file_path):
    return os.path.basename(rhd_file_path).split('.')[0]

def compute_samples_per_position(pos_sample_rate):
    eeg_sample_rate = 250
    egf_sample_rate = 4.8e3

    eeg_samples_per_position = eeg_sample_rate / pos_sample_rate
    egf_samples_per_position = egf_sample_rate / pos_sample_rate

    return eeg_samples_per_position, egf_samples_per_position

