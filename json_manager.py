import json
import os

from cryptography.fernet import Fernet


def load_user_data(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as json_file:
            json.dump({}, json_file)
    with open(file_name, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def save_user_data(file_name, data):
    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)


def decrypt_password(data):
    # 비밀번호 복호화
    if data["login_info"][1]:
        key = data["login_info"][2].encode()
        cipher_suite = Fernet(key)
        decrypted_password = cipher_suite.decrypt(data["login_info"][1].encode())
        data["login_info"][1] = decrypted_password.decode()


def encrypt_password(data):
    # 비밀번호 암호화
    if data["login_info"][1]:
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(data["login_info"][1].encode())
        data["login_info"][1] = encrypted_password.decode()
        data["login_info"][2] = key.decode()
