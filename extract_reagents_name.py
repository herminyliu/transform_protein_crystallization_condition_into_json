import csv
import ast
import pandas as pd

# 读取CSV文件
input_csv_file = './deepseek/output_5.csv'  # 替换为你的输入CSV文件路径
output_csv_file = './deepseek/reagents_name.csv'  # 替换为你的输出CSV文件路径

# 使用pandas读取CSV文件
df = pd.read_csv(input_csv_file)

# 提取exptl_crystal_grow.pdbx_details_extracted.reagents列
reagents_column = df['exptl_crystal_grow.pdbx_details_extracted.reagents']

# 用于存储所有键的集合
all_keys = set()

# 遍历该列中的每个元素
for reagent in reagents_column:
    if pd.notna(reagent):  # 检查是否为NaN
        try:
            # 使用 ast.literal_eval 解析 Python 字典字符串
            reagent_dict = ast.literal_eval(reagent)
            # 提取键并添加到集合中
            all_keys.update(reagent_dict.keys())
        except (ValueError, SyntaxError) as e:
            print(f"Invalid format: {reagent}")
            print(f"Error: {e}")

# 将集合转换为列表并按字母顺序排序
sorted_keys = sorted(all_keys, key=lambda x: x.lower())

# 将排序后的键写入新的CSV文件
with open(output_csv_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for key in sorted_keys:
        writer.writerow([key])

print(f"All keys have been written to {output_csv_file}")