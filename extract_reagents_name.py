import csv
import ast
import pandas as pd

# 读取CSV文件
input_csv_file = './deepseek/output_15-300.csv'  # 替换为你的输入CSV文件路径
output_csv_file = './deepseek/reagents_name.csv'  # 替换为你的输出CSV文件路径

# 使用pandas读取CSV文件
df = pd.read_csv(input_csv_file)

# 提取exptl_crystal_grow.pdbx_details_extracted.reagents列
reagents_column = df['exptl_crystal_grow.pdbx_details_extracted.reagents']

# 用于存储小写形式的键（用于去重）
lowercase_keys_set = set()

# 用于存储原始格式的键
original_keys_list = []

# 遍历该列中的每个元素
for reagent in reagents_column:
    if pd.notna(reagent):  # 检查是否为NaN
        try:
            # 使用 ast.literal_eval 解析 Python 字典字符串
            reagent_dict = ast.literal_eval(reagent)
            # 提取键并处理
            for key in reagent_dict.keys():
                lowercase_key = key.lower()  # 转换为小写
                if lowercase_key not in lowercase_keys_set:  # 如果小写键不存在，则存储
                    lowercase_keys_set.add(lowercase_key)  # 添加到 set 中
                    original_keys_list.append(key)  # 保留原始格式的键
        except (ValueError, SyntaxError) as e:
            print(f"Invalid format: {reagent}")
            print(f"Error: {e}")

# 将原始格式的键按字母顺序排序
sorted_keys = sorted(original_keys_list, key=lambda x: x.lower())

# 将排序后的键写入新的CSV文件
with open(output_csv_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for key in sorted_keys:
        writer.writerow([key])

print(f"All keys have been written to {output_csv_file}")