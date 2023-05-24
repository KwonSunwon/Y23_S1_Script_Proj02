import json
import os


def load_user_data(fileName):
    if not os.path.exists(fileName):
        with open(fileName, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(fileName, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def save_user_data(fileName, data):
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(data, f)
