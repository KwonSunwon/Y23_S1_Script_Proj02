import json
from cryptography.fernet import Fernet


# 암호화를 위한 키 생성
key = Fernet.generate_key()
cipher_suite = Fernet(key)
print("암호화 키:", key)


def save():
    # 비밀번호 입력 받기
    password = input("비밀번호를 입력하세요: ")

    # 비밀번호를 바이트로 변환
    password_bytes = password.encode()

    # 비밀번호를 암호화
    encrypted_password = cipher_suite.encrypt(password_bytes)

    # 암호화된 비밀번호를 JSON 데이터로 저장
    data = {"password": encrypted_password.decode()}

    # JSON 파일로 저장
    with open("passwords.json", "w") as file:
        json.dump(data, file)


def load():
    # JSON 파일에서 데이터 읽어오기
    with open("passwords.json", "r") as file:
        data = json.load(file)

    # 암호화된 비밀번호 가져오기
    encrypted_password = data["password"]

    # 비밀번호를 복호화
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode())

    # 복호화된 비밀번호 출력
    password = decrypted_password.decode()
    print("복호화된 비밀번호:", password)


save()
load()
