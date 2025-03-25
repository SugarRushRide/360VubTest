import os
import re
from time import sleep
from colorama import Fore, Style
import pytest
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 从环境变量中读取参数
indicator = os.getenv("INDICATOR")
school_name = os.getenv("SCHOOL_NAME")
value = os.getenv("VALUE")
year = os.getenv("YEAR")

# 打印参数（可选，用于调试）
# print(f"Indicator: {indicator}, School Name: {school_name}, Value: {value}, Year: {year}")


@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Edge()
    # 测试环境
    driver.get("https://cg-3f3ab907.gaojidata.com/login")
    # 正式环境
    # driver.get("https://cg-beta.gaojidata.com/login")
    # 设置浏览器为全屏模式
    driver.maximize_window()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "LoginName")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Password")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_btn")))
        print("登录页面加载成功!")
    except:
        print("超时,登录页面加载失败!")

    jump_to_gaojidata(driver)

    yield driver
    print("所有测试完成，退出浏览器")

    driver.quit()


def jump_to_gaojidata(driver):
    # 账号信息
    account = "chengjun.jiang"
    password = "shanghai0303"

    # 登录
    driver.find_element(By.ID, "LoginName").send_keys(account)
    driver.find_element(By.ID, "Password").send_keys(password)
    driver.find_element(By.ID, "login_btn").click()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "vub-jump")))
        print("home页面加载成功!")
    except:
        print("超时,home页面加载失败!")

    # 进入高职360页面
    driver.find_element(By.ID, "vub-jump").click()
    try:
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "rc_select_0")))
        print("高职360员工页面加载成功!")
    except:
        print("超时,高职360员工页面加载失败!")


def create_account(driver, school_name):
    # 创建学校账号
    driver.find_element(By.ID, "add_acount_btn").click()

    # 保存按钮
    save = f"//div[@class='ant-modal-content']//div[@class='button-box']/button[span[contains(text(), '保 存')]]"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "univCode")))
    select = driver.find_element(By.ID, "univCode")
    select.send_keys(school_name)
    select.send_keys(Keys.ENTER)
    driver.find_element(By.XPATH, save).click()


# 从数据行中提取数据
def extract_data(cell):
    try:
        # 1. 处理情况 1 和 2：获取最里层文本内容
        span = cell.find_elements(By.XPATH, ".//span")
        if span:
            return span[-1].text.strip()  # 获取最里层的文本

        # 2. 处理情况 3：处理嵌套结构，获取所有文本
        text = cell.text.strip()
        if text:
            return text
    except NoSuchElementException:
        # 3. 处理情况 4：获取 span 的 title 属性（没有数据时显示为“-”）
        title = cell.find_element(By.XPATH, ".//span[@title]").get_attribute("title")
        if title:
            return title

        # 4. 处理情况 5：提取 SVG 图标中的 fill-opacity
        svg = cell.find_elements(By.XPATH, ".//svg")
        if svg:
            style = svg[0].get_attribute("style")
            if style:
                # 提取 fill-opacity
                match = re.search(r"fill-opacity:\s*(\d+(\.\d+)?)", style)
                if match:
                    return match.group(1)  # 返回 fill-opacity 的值

    # 如果无法处理，返回空
    return None


# 全部指标页面查看监测年份
def check_year_in_all_ind(driver):
    global year
    # 打开监测年份窗口
    window = f"//input[@placeholder='选择年份']"
    driver.find_element(By.XPATH, window).click()
    # 查找当前选择监测年份
    current_year_path = f"//div//ul[@class='picker-date-list']/li[@class='active-item']/span"
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, current_year_path)))
    current_year = driver.find_element(By.XPATH, current_year_path).text.strip()
    # print("当前年份："+current_year)
    # 年份调整
    # print("当前年份:"+current_year+";目标年份:"+year)
    if year != current_year:
        current_year = alter_year_in_all_ind(driver)
    driver.find_element(By.XPATH, window).click()
    # print("返回年份："+current_year)
    return current_year


# 全部指标页面年份调整
def alter_year_in_all_ind(driver):
    global year
    window = f"//input[@placeholder='选择年份']"
    target_year_path = f"//div//ul[@class='picker-date-list']/li/span[contains(text(), '{year}')]"
    year_element = driver.find_element(By.XPATH, target_year_path)
    class_value = year_element.get_attribute("class")
    # 若目标年份为disable-item,抛出异常
    assert "disable-item" not in class_value, f"目标年份{year}不可选,数据尚未更新或出现其他异常!"
    driver.find_element(By.XPATH, target_year_path).click()
    driver.find_element(By.XPATH, window).click()
    return year

# 百分数转为小数
def percent_to_float(percent_str):
    return float(percent_str[:-1]) / 100

def is_equal(float1, float2, tolerance=1e-6):
    return abs(float(float2) - float(float1) < tolerance)

def test_jump_to_target_school(driver):
    global school_name
    input_box = driver.find_element(By.ID, "rc_select_0")
    # 输入学校名
    input_box.send_keys(school_name)
    # 回车确认
    input_box.send_keys(Keys.ENTER)

    # 不存在目标学校账号
    sleep(1)
    exist = f"//tr[td[contains(text(), '{school_name}')]]//div[@class='operate']/span[contains(text(), '跳转')]"
    elements = driver.find_elements(By.XPATH, exist)
    # driver.find_element(By.XPATH, "//div[@class='ant-table-content']//div[@class='ant-empty-image']/p[contains(text, '暂无数据')]")

    # 学校不存在,创建账号
    if not elements:
        print(school_name + "不存在,将创建账号")
        create_account(driver, school_name)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, exist)))
        elements = driver.find_elements(By.XPATH, exist)

    # 存在目标学校账号
    # 选择第一条进行跳转
    print(school_name + "存在,即将跳转...")
    # 记录点击前窗口句柄
    original_window = driver.current_window_handle
    # 跳转
    elements[0].click()
    # 等待跳转
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
    # 切换到新窗口
    new_window = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_window)
    # 等待URL变化
    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
    # 断言新URL是否正确
    # 测试环境
    expected_url = "https://vub-3f3ab907.gaojidata.com/overview"
    # 正式环境
    # expected_url = "https://vub.gaojidata.com/overview"
    assert driver.current_url == expected_url, f"URL错误,跳转失败,当前 URL: {driver.current_url}"
    print("成功跳转至" + school_name)


def test_data_overall(driver):
    ind_chose = f"//span[span[contains(text(), '指标')]]/span[@class='filter-icon']/*"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ind_chose)))

    # 指标搜索
    ind_filter = driver.find_element(By.XPATH, ind_chose)

    # 执行JS脚本点击svg元素
    # driver.execute_script("arguments[0],click();", filter)
    # 用ActionChains
    ActionChains(driver).move_to_element(ind_filter).click().perform()
    input_ind = f"//input[@placeholder='请输入搜索关键字']"
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, input_ind)))
    search = driver.find_element(By.XPATH, input_ind)
    search.send_keys(indicator)
    search.send_keys(Keys.ENTER)

    # 选择指标
    ind_select = f"//label[@class='ant-checkbox-wrapper']/span[input[@type='checkbox']]"
    try:
        driver.find_element(By.XPATH, ind_select).click()
    except NoSuchElementException:
        assert False, f"该指标为非排名指标,总体定位页面无该数据"
        # raise AssertionError("该指标为非排名指标,总体定位页面无该数据")

        # pytest.fail("该指标为非排名指标,总体定位页面无该数据", pytrace=False)
    verify = f"//button[span[contains(text(), '确认')]]"
    driver.find_element(By.XPATH, verify).click()

    # 数据提取
    # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class='custom-name']")))
    headers = [header.text.strip() for header in driver.find_elements(By.XPATH, "//span[@class='custom-name']")]
    # print(headers)
    rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
    data_dict_list = []
    for row in rows:
        cells = row.find_elements(By.XPATH, ".//td")
        row_data = [extract_data(cell) for cell in cells]
        # print(row_data)
        row_dict = dict(zip(headers, row_data))
        if row_dict["指标数据"].endswith("%"):
            row_dict["指标数据"] = percent_to_float(row_dict["指标数据"])
        data_dict_list.append(row_dict)
        print(row_dict)

    assert year == data_dict_list[0][
        "监测年份"], f"检测年份有误,页面中为{data_dict_list[0]["监测年份"]},数据更新检测年份为{year},无法核验数据!"
    assert is_equal(value, data_dict_list[0]["指标数据"]), f"指标数据有误!请查找问题原因!!"
    # print("总体定位页面" + indicator + "指标数据更新核验完毕,未发现问题")
    '''输出'''
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)
    # 标题
    print(Fore.GREEN + "总体定位页面" + Style.RESET_ALL)
    # 内容
    print(
        f"{Fore.GREEN}指标: {Fore.YELLOW}{indicator}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}页面数据: {Fore.CYAN}{data_dict_list[0]["指标数据"]}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}校对数据: {Fore.CYAN}{value}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}状态: {Fore.GREEN}✔ 未发现问题~{Style.RESET_ALL}"
    )
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)

# 全部指标页面数据核验
def test_data_all_ind(driver):
    global value
    global school_name
    global indicator
    all_ind = f"//*[@id='sub_menu_3_$$_univ-data-popup']/div[2]/li/span/div/div"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, all_ind)))

    # 跳转至全部指标页面
    driver.find_element(By.XPATH, all_ind).click()
    sleep(2)

    # 等待页面加载
    # ind_chose = f"//section/section/main//table/thead//span[contains(., '指标')]/span[@class='filter-icon']/*"
    ind_chose = f"//section/section/main/div/div[2]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div[1]/table/thead/tr/th[3]/div/span/span[2]/*"
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ind_chose)))

    # 指标搜索
    ind_filter = driver.find_element(By.XPATH, ind_chose)
    # 用ActionChains
    sleep(1)
    ActionChains(driver).move_to_element(ind_filter).pause(1).click().perform()
    # 如果 ActionChains 失败，尝试 JavaScript
    # driver.execute_script("arguments[0].click();", ind_filter)
    input_ind = f"//div//input[@placeholder='请输入搜索关键字']"
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, input_ind)))
    search = driver.find_element(By.XPATH, input_ind)
    search.send_keys(indicator)
    search.send_keys(Keys.ENTER)

    # 选择指标
    ind_select = f"//label[@class='ant-checkbox-wrapper']/span[input[@type='checkbox']]"
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, ind_select)))
    driver.find_element(By.XPATH, ind_select).click()
    verify = f"//button[span[contains(text(), '确认')]]"
    driver.find_element(By.XPATH, verify).click()

    # 年份选择,若年份非数据更新年份,则进行调整
    current_year = check_year_in_all_ind(driver)

    # 提取数据
    sleep(1)
    WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class='custom-name']")))
    # 提取最里层文本"//th[contains(@class, 'vxe-header--column')]//*[self::div or self::span][not(*) and normalize-space()]"
    headers = [header.text.strip() for header in driver.find_elements(By.XPATH,
                                                                      "//th[contains(@class, 'vxe-header--column')]//span[@class='custom-name'] | //th[contains(@class, 'vxe-header--column')]//div[@class='none-border']")]
    # print(headers)
    values = [value.text.strip() for value in driver.find_elements(By.XPATH,
                                                                   "//td[contains(@class, 'vxe-body--column')]//*[self::div or self::span][(not(*) or @title='未公布') and not(contains(., '重置'))]")]
    for i in range(len(values)):
        if values[i] == "":
            values[i] = "0.00"
    # print(values)

    # 提取当前监测年份数据
    if len(headers) > len(values):
        # current_year = check_year_in_all_ind(driver)
        year_index = headers.index("监测年份")
        values.insert(year_index, current_year)
        # print(values)

    # 存为字典
    data_dict = dict(zip(headers, values))
    if data_dict[school_name].endswith("%"):
        data_dict[school_name] = percent_to_float(data_dict[school_name])
    print(data_dict)

    # 数据核验
    assert is_equal(value, data_dict[school_name]), f"指标数据有误!页面数据为:{data_dict[school_name]},校对数据为:{value}.请查找问题原因!!"
    # print("全部指标页面" + indicator + "指标数据更新核验完毕,页面数据为:" + str(data_dict[school_name]) + ",校对数据为:" + value + ",未发现问题~")
    '''输出'''
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)
    # 标题
    print(Fore.GREEN + "全部指标页面" + Style.RESET_ALL)
    # 内容
    print(
        f"{Fore.GREEN}指标: {Fore.YELLOW}{indicator}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}页面数据: {Fore.CYAN}{str(data_dict[school_name])}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}校对数据: {Fore.CYAN}{value}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}状态: {Fore.GREEN}✔ 未发现问题~{Style.RESET_ALL}"
    )
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)


# 指标查看页面数据核验
def test_data_ind_check(driver):
    global value
    global year
    global indicator
    ind_check = f"//*[@id='sub_menu_3_$$_univ-data-popup']/div[1]/li/span"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ind_check)))

    # 跳转至指标查看页面
    driver.find_element(By.XPATH, ind_check).click()
    ind_chose = f"//input[@placeholder='搜索/选择']"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ind_chose)))
    ActionChains(driver).click(driver.find_element(By.XPATH, ind_chose)).send_keys(indicator).perform()
    ind_select = f"//div[@class='search-result-box']//li[@title='{indicator}']"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ind_select)))
    driver.find_element(By.XPATH, ind_select).click()

    # 勾选查看本校和标杆
    check_self = f"//label[span[contains(., '查看本校和标杆')]]/span[@class='ant-checkbox']"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, check_self)))
    driver.find_element(By.XPATH, check_self).click()
    sleep(1)

    # 提取数据
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class='custom-name']")))
    # 提取最里层文本"//th[contains(@class, 'vxe-header--column')]//*[self::div or self::span][not(*) and normalize-space()]"
    headers = [header.text.strip() for header in driver.find_elements(By.XPATH,
                                                                      "//th[contains(@class, 'vxe-header--column')]//*[self::div or self::span][not(*) and normalize-space()]")]
    # print(headers)
    values = [value.text.strip() for value in driver.find_elements(By.XPATH,
                                                                   "//td[contains(@class, 'vxe-body--column')]//*[self::div or self::span][not(*) and normalize-space()]")]
    # values = driver.find_elements(By.XPATH,"//td[contains(@class, 'vxe-body--column')]//*[self::div or self::span][not(*) and normalize-space() and not(contains(., '重置'))]")
    # print(values)
    # 存为字典
    data_dict = dict(zip(headers, values))
    if data_dict[year].endswith("%"):
        data_dict[year] = percent_to_float(data_dict[year])
    # print(data_dict)

    # 核验数据正确性
    assert year in data_dict, f"未找到数据项,是否未更新?"
    assert is_equal(value, data_dict[year]), f"指标数据有误!页面数据为:{data_dict[year]},校对数据为:{value}.请查找问题原因!!"
    # print("指标查看页面" + indicator + "指标数据更新核验完毕,页面数据为:" + str(data_dict[year]) + ",校对数据为:" + value + ",未发现问题~")
    '''输出'''
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)
    # 标题
    print(Fore.GREEN + "指标查看页面" + Style.RESET_ALL)
    # 内容
    print(
        f"{Fore.GREEN}指标: {Fore.YELLOW}{indicator}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}页面数据: {Fore.CYAN}{str(data_dict[year])}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}校对数据: {Fore.CYAN}{value}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}状态: {Fore.GREEN}✔ 未发现问题~{Style.RESET_ALL}"
    )
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)


# 数据反馈页面数据核验
def test_data_feedback(driver):
    global value
    global year
    global indicator
    feedback = f"//span[contains(.,'数据反馈')]"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, feedback)))
    driver.find_element(By.XPATH, feedback).click()
    # ind_filter = f"/html/body/div[1]/section/section/main/div/div[2]/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div[1]/table/thead/tr/th[3]/div/span/span[2]/*"
    ind_filter = f"//section/section//thead//span[span[contains(text(),'指标')]]/span[@class='filter-icon']/*"
    sleep(2)
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, ind_filter)).pause(1).click().perform()

    input_ind = f"//div//input[@placeholder='请输入搜索关键字']"
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, input_ind)))
    search = driver.find_element(By.XPATH, input_ind)
    search.send_keys(indicator)
    search.send_keys(Keys.ENTER)

    # 选择指标
    ind_select = f"//label[@class='ant-checkbox-wrapper']/span[input[@type='checkbox']]"
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, ind_select)))
    driver.find_element(By.XPATH, ind_select).click()
    verify = f"//button[span[contains(text(), '确认')]]"
    driver.find_element(By.XPATH, verify).click()

    # 年份选择,若年份非数据更新年份,则进行调整
    current_year = check_year_in_all_ind(driver)

    # 提取数据
    sleep(1)
    WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class='custom-name']")))
    # 提取最里层文本"//th[contains(@class, 'vxe-header--column')]//*[self::div or self::span][not(*) and normalize-space()]"
    headers = [header.text.strip() for header in driver.find_elements(By.XPATH,
                                                                      "//th[contains(@class, 'vxe-header--column')]//span[@class='custom-name'] | //th[contains(@class, 'vxe-header--column')]//div[@class='none-border']")]
    # print(headers)
    values = [value.text.strip() for value in driver.find_elements(By.XPATH,
                                                                   "//td[contains(@class, 'vxe-body--column')]//*[self::div or self::span][(not(*) or @title='未公布') and not(contains(., '重置'))]")]
    for i in range(len(values)):
        if values[i] == "":
            values[i] = "未公布"
    # print(values)

    # 提取当前监测年份数据
    if len(headers) > len(values):
        # current_year = check_year_in_all_ind(driver)
        year_index = headers.index("监测年份")
        values.insert(year_index, current_year)
        # print(values)

    # 存为字典
    data_dict = dict(zip(headers, values))
    if data_dict["监测年份"].endswith("%"):
        data_dict["监测年份"] = percent_to_float(data_dict["监测年份"])
    # print(data_dict)

    # 总页面数据核验
    assert is_equal(value, data_dict["监测年份"]), f"指标数据有误!页面数据为:{data_dict["监测年份"]},校对数据为:{value}.请查找问题原因!!"
    # print("数据反馈页面" + indicator + "指标数据更新核验完毕,页面数据为:" + str(data_dict["监测年份"]) + ",校对数据为:" + value + ",未发现问题~")
    '''输出'''
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)
    # 标题
    print(Fore.GREEN + "数据反馈页面" + Style.RESET_ALL)
    # 内容
    print(
        f"{Fore.GREEN}指标: {Fore.YELLOW}{indicator}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}页面数据: {Fore.CYAN}{data_dict["监测年份"]}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}校对数据: {Fore.CYAN}{value}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}状态: {Fore.GREEN}✔ 未发现问题~{Style.RESET_ALL}"
    )
    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)

    # 数据反馈操作页面数据核验
    operation = f"//span[contains(.,'数据反馈') and @class='link-a']"
    driver.find_element(By.XPATH, operation).click()

    # 提取数据
    sleep(1)
    data_path = f"//div[@class='table-layout']//tr"
    elements = driver.find_elements(By.XPATH, data_path)
    data_dict_2 = {}
    for element in elements:
        tds = element.find_elements(By.TAG_NAME, "td")
        if len(tds) >= 2:  # 确保至少有两列
            key = tds[0].text.strip()  # 第一列作为键
            val = " ".join(td.text.strip() for td in tds[1:])  # 其余列合并为值
            data_dict_2[key] = val

    if data_dict_2["当前数据"].endswith("%"):
        data_dict_2["当前数据"] = percent_to_float(data_dict_2["当前数据"])
    print(data_dict_2)  # 输出字典
    assert is_equal(value, data_dict_2["当前数据"]), f"指标数据有误!页面数据为:{data_dict_2["当前数据"]},校对数据为:{value}.请查找问题原因!!"
    # print("数据反馈页面" + indicator + "指标数据更新核验完毕,页面数据为:" + str(data_dict_2[
    #     "当前数据"]) + ",校对数据为:" + value + ",未发现问题~")

    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)

    # 标题
    print(Fore.GREEN + "数据反馈页面核验结果" + Style.RESET_ALL)

    # 内容
    print(
        f"{Fore.GREEN}指标: {Fore.YELLOW}{indicator}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}页面数据: {Fore.CYAN}{data_dict_2['当前数据']}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}校对数据: {Fore.CYAN}{value}{Style.RESET_ALL}\n"
        f"{Fore.GREEN}状态: {Fore.GREEN}✔ 未发现问题~{Style.RESET_ALL}"
    )

    # 分隔线
    print(Fore.BLUE + "=" * 80 + Style.RESET_ALL)
