import os
import subprocess

test_data = [
    ("国际期刊论文", "江西职业技术大学", "69", "2024"),
    ("国际期刊论文", "金华职业技术大学", "536", "2024"),
    ("本省就业率（本科）", "上海中侨职业技术大学", "0.8037", "2023"),
    ("毕业去向落实率（本科）", "广西农业职业技术大学", "0", "2023"),
    ("本省就业率（本科）", "重庆机电职业技术大学", "0.59809", "2023"),
    ("毕业去向落实率（本科）", "新疆天山职业技术大学", "0.9402", "2023"),
]

for data in test_data:
    indicator, school_name, value, year = data
    # 设置环境变量
    os.environ["INDICATOR"] = indicator
    os.environ["SCHOOL_NAME"] = school_name
    os.environ["VALUE"] = value
    os.environ["YEAR"] = year
    # 运行 pytest
    os.system('pytest -s test_data_accuracy.py')