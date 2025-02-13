import requests
import csv
import json
import sys
from datetime import datetime


def send_request(query_file, variables_file):
    # 读取query部分
    with open(query_file, 'r', encoding='utf-8') as f:
        query = f.read()

    # 读取变量部分并格式化为JSON字符串
    with open(variables_file, 'r', encoding='utf-8') as f:
        ids = [line.strip() for line in f if line.strip()]
        variables = json.dumps({"ids": ids})

    url = 'https://data.rcsb.org/graphql'
    headers = {
        'Content-Type': 'application/json'
    }

    # 构造请求的payload
    payload = {
        'query': query,
        'variables': variables
    }

    # 发送GET请求
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # 确保请求成功
    return response.json()


def process_response_to_csv(response_data):
    # 提取response中的字段并生成CSV文件
    entries = response_data.get('data', {}).get('entries', [])
    if not entries:
        print("No data found.")
        return

    # 获取列名：遍历第一个entry获取动态的列名
    first_entry = entries[0]
    column_names = []

    def generate_col(key, value, col_name):
        columns = []
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                full_col_name = f"{col_name}.{sub_key}"
                columns.extend(generate_col(sub_key, sub_value, full_col_name))
        elif isinstance(value, list):
            if value and isinstance(value[0], (dict, list)):
                for item in value:
                    columns.extend(generate_col(key, item, col_name))
                    # 使用 extend() 是为了确保将每次递归调用返回的所有列名扁平化地添加到 columns 列表中
            else:
                columns.append(col_name)
        else:
            columns.append(col_name)

        return columns

    # 示例调用
    column_names = []
    for key, value in first_entry.items():
        column_names.extend(generate_col(key, value, key))

    # 生成CSV文件路径
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_filename = f"./1104-try/{timestamp}.csv"

    # 写入CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)

        for entry in entries:
            row = []
            for col in column_names:
                keys = col.split('.')
                value = entry
                for key in keys:
                    if isinstance(value, list) and value:
                        value = value[0]  # 处理嵌套列表中的第一个元素
                    value = value.get(key) if isinstance(value, dict) else None
                    if value is None:
                        break
                row.append(value)
            writer.writerow(row)

    print(f"Data successfully written to {csv_filename}")


if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) != 3:
        print("Usage: python script.py <query_file> <variables_file>")
        sys.exit(1)

    query_file = sys.argv[1]
    variables_file = sys.argv[2]

    # 发送请求并处理响应
    try:
        response_data = send_request(query_file, variables_file)
        process_response_to_csv(response_data)
    except Exception as e:
        print(f"Error occurred: {e}")

