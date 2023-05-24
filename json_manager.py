"""json_manager.py"""

import json
import os


def load_user_data(file_name):
    """사용자 데이터를 불러옵니다."""
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as json_file:
            json.dump({}, json_file)
    with open(file_name, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def save_user_data(file_name, data):
    """사용자 데이터를 저장합니다."""
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)
