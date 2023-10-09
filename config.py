import json

def get_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print('설정 파일이 존재하지 않습니다.')