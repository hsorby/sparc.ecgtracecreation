
import os
import json


def read_data(file_name):
    data = {}
    if os.path.exists(file_name) and os.path.isfile(file_name):
        with open(file_name) as f:
            content = f.read()
            data = json.loads(content)

    return data
