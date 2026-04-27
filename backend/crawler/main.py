# python3/main.py
from pathlib import Path
import json 

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / 'config.json'




# 读取配置文件
def read_config():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    return config



# 自动抓取需要下载的 url
def get_downloading_list(config: dict) -> list[dict]:
    pass


# 下载
def download(l: list[dict]):
    # 下载

    # 校验

    pass



# 下载结果整理保存
def parse_result(config: dict, downloading_list: list[dict]):
    pass


# 主函数
# 后续很可能需要改为异步
def main():
    config = read_config()

    downloading_list = get_downloading_list(config=config)
    
    download(downloading_list)

    parse_result(config=config, downloading_list=downloading_list)


if __name__ == "__main__":
    main()