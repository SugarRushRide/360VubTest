import os

test_data = [
    # ("本省就业率", "泉州职业技术大学", "0.8966", "2023"),
    # ("毕业去向落实率", "西安信息职业大学", "0.8608", "2022"),
    # ("本省就业率（本科）", "新疆天山职业技术大学", "0.9023", "2023"),
    # ("毕业生成长", "南昌职业大学", "0.325", "2021"),
    # ("技术服务到款", "河南科技职业大学", "0", "2022"),
    # ("培训服务到款", "河南科技职业大学", "22", "2022"),
    # ("留学生数", "山东外国语职业技术大学", "346", "2023"),
    # ("党建工作示范单位", "山东外国语职业技术大学", "1", "2023"),
    # ("省级课程思政项目", "山东外国语职业技术大学", "3", "2023"),
    # ("模范先进学生（折合数）", "金华职业技术大学", "0", "2020"),
    ("国家级课程思政项目", "浙江机电职业技术大学", "1", "2021")
]

for data in test_data:
    indicator, school_name, value, year = data
    # 设置环境变量
    os.environ["INDICATOR"] = indicator
    os.environ["SCHOOL_NAME"] = school_name
    os.environ["VALUE"] = value
    os.environ["YEAR"] = year
    # 运行 pytest
    os.system('pytest test_data_accuracy.py -s')