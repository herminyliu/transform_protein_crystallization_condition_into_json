import requests
import json
import sys
import os
from datetime import datetime


def send_request(query_json):
    url = f"https://search.rcsb.org/rcsbsearch/v2/query"

    # 发送POST请求
    response = requests.post(url=url, json=query_json)
    response.raise_for_status()  # 确保请求成功
    return response.json()


def save_identifiers_to_file(result_set, output_file):
    identifiers = [entry['identifier'] for entry in result_set]

    with open(output_file, 'w', encoding='utf-8') as f:
        for identifier in identifiers:
            f.write(f"{identifier}\n")

    print(f"Identifiers successfully saved to {output_file}")


if __name__ == "__main__":
    # 检查命令行输入参数数量是否足够
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_json_file> [<output_txt_file>]")
        sys.exit(1)

    input_json_file = sys.argv[1]

    # 设置默认输出文件名
    if len(sys.argv) == 3:
        output_txt_file = sys.argv[2]
    else:
        if not os.path.exists("./identifier_lst/"):
            os.makedirs("./identifier_lst/")
        timestamp = datetime.now().strftime("./identifier_lst/%Y%m%d-%H%M%S")
        output_txt_file = f"{timestamp}.txt"

    # 读取输入的JSON文件
    with open(input_json_file, 'r', encoding='utf-8') as f:
        query_json = json.load(f)

    # 发送请求并处理响应
    response_data = send_request(query_json)
    result_set = response_data.get('result_set', [])
    save_identifiers_to_file(result_set, output_txt_file)
    try:
        response_data = send_request(query_json)
        result_set = response_data.get('result_set', [])
        save_identifiers_to_file(result_set, output_txt_file)
    except Exception as e:
        print(f"Error occurred: {e}")
