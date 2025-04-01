import json
import os
import subprocess
import re

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
    # ("国家级课程思政项目", "浙江机电职业技术大学", "1", "2021"),
    # ("全日制在校生数", "景德镇艺术职业大学", "17644", "2023"),
    # ("全日制在校生数", "北京交通职业技术学院", "999", "2023"),
    # ("全日制在校生数", "上海中侨职业技术大学", "9316", "2023"),
    # 2025-4-1
    ("本省就业率", "齐齐哈尔高等师范专科学校", "0.1835", "2023"),
    ("学校总收入", "福建幼儿师范高等专科学校", "17174.97", "2023"),
    ("教师规模", "山西警官职业学院", "73", "2023"),
    ("教师职称结构", "民办合肥经济技术职业学院", "0.1458", "2023"),
    ("培训服务到款", "甘肃钢铁职业技术学院", "534.068", "2023"),
    ("双师型教师比例", "漳州理工职业学院", "0.3368", "2023"),
    ("毕业生成长", "喀什职业技术学院", "0", "2023"),
    ("培训服务到款", "湖南网络工程职业学院", "0", "2023"),
    ("高水平科技论文", "上海中侨职业技术大学", "98", "2024"),
    ("高水平科技论文", "西安信息职业大学", "1", "2024"),
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

# 存储所有测试报告的路径
# report_files = ["/test_report_files"]
#
# for index, data in enumerate(test_data, start=1):
#     indicator, school_name, value, year = data
#
#     # 设置环境变量
#     os.environ["INDICATOR"] = indicator
#     os.environ["SCHOOL_NAME"] = school_name
#     os.environ["VALUE"] = value
#     os.environ["YEAR"] = year
#
#     # 生成 HTML 报告的路径
#     report_file = os.path.join("/test_report_files", f"test_report_{index}.html")
#     report_files.append(report_file)
#
#     print(f"\n【执行测试 {index}/{len(test_data)}】：{indicator} - {school_name}")
#
#     # 运行 pytest，并生成独立的 HTML 报告
#     subprocess.run(
#         [
#             "pytest", "test_data_accuracy.py",
#             "--html=" + report_file,
#             "--self-contained-html",
#             "-s"
#         ]
#     )
#
# # 生成索引页
# index_html_path = os.path.join("/test_report_files", "index.html")
# with open(index_html_path, "w", encoding="utf-8") as index_file:
#     index_file.write("<html><head><title>测试报告索引</title></head><body>")
#     index_file.write("<h1>测试报告索引</h1><ul>")
#
#     for report in report_files:
#         index_file.write(f'<li><a href="{os.path.basename(report)}">{os.path.basename(report)}</a></li>')
#
#     index_file.write("</ul></body></html>")
#
# print(f"\n📊 测试完成！所有报告已生成，查看索引页: {index_html_path}")







