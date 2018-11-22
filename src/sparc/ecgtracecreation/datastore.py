import os
import json


def save_data(file_name, data):
    with open(file_name, 'w') as f:
        data_in_string_form = json.dumps(data)
        f.write(data_in_string_form)


def get_complementary_file_name(file_name):
    file_path, file_head = os.path.split(file_name)
    file_stem, file_ext = os.path.splitext(file_head)
    return os.path.join(file_path, 'ecg_electrode_data' + file_ext)
