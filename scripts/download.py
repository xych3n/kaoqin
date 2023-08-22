"""
Automated script for downloading and processing activity records from the
legacy system. This script downloads .xls files for different categories
of activities and extracts relevant information for analysis and reporting.

Dependencies:
- xlrd
- xlwt
- selenium

Usage:
- Adjust login credentials, URLs, and other settings as needed.
- Customize the directory for downloaded files if required.

Note:
- Passwords have been removed from this script for security reasons. (Line 46-47)
"""

import os
import re
from datetime import date, datetime, timedelta
from typing import Sequence

import xlrd, xlwt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download_all(directory):
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"download.default_directory" : os.path.abspath(directory)}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(options=options)

    driver.get("http://10.20.8.129:66/Login.aspx")
    username_xpath = '//*[@id="ff"]/table/tbody/tr[1]/td[2]/span/input[1]'
    password_xpath = '//*[@id="ff"]/table/tbody/tr[2]/td[2]/span/input[1]'
    login_xpath = '//*[@id="ContentPlaceHolder1_btnLogin"]/span/span'

    accounts = [
        ("admin", "", "学术讲座"),
        ("yanhui", "", "研会活动"),
    ]
    for username, password, category in accounts:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, username_xpath))
        ).send_keys(username)
        driver.find_element(By.XPATH, password_xpath).send_keys(password)
        driver.find_element(By.XPATH, login_xpath).click()
        driver.implicitly_wait(1)
        driver.switch_to.alert.accept()
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_downloadbtn"))
        ).click()
        filename = "{}_{}.xls".format(category, datetime.today().strftime("%Y%m%d"))
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        found = False
        while not found:
            for back_allowance in (0, 1):
                t = datetime.now() - timedelta(minutes=back_allowance)
                expected_filename = f"刷卡统计-汇总表（截止至{t.year}年{t.month}月{t.day}日 {t.hour}_{t.minute:02}）.xls"
                expected_filepath = os.path.join(directory, expected_filename)
                if os.path.exists(expected_filepath):
                    os.rename(expected_filepath, filepath)
                    found = True
                    break
        driver.find_element(value="ContentPlaceHolder1_LinkButton1").click()


def extract(book, sheet_name: str, cols: Sequence[int]):
    sh = book.sheet_by_name(sheet_name)
    for i in range(1, sh.nrows):
        yield [sh.cell_value(i, j) for j in cols]


def save(filename, data_count, data_detail):
    book = xlwt.Workbook()
    # sheet1
    sh = book.add_sheet("次数统计")
    headers = ["学号", "姓名", "次数"]
    for j, header in enumerate(headers):
        sh.write(0, j, header)
    for i, row in enumerate(data_count, start=1):
        for j, val in enumerate(row):
            sh.write(i, j, val)
    # sheet2
    sh = book.add_sheet("记录明细")
    headers = ["学号", "姓名", "活动", "日期", "次数"]
    for j, header in enumerate(headers):
        sh.write(0, j, header)
    for i, row in enumerate(data_detail, start=1):
        for j, val in enumerate(row):
            sh.write(i, j, val)
    #
    book.save(filename)


if __name__ == "__main__":
    download_directory = "."
    download_all(download_directory)

    filename = "学术讲座_{}.xls".format(datetime.today().strftime("%Y%m%d"))
    book = xlrd.open_workbook(os.path.join(download_directory, filename))
    data_count = list(extract(book, "记录统计", (0, 1, 2)))
    data_detail = []
    for row in extract(book, "记录明细", (0, 2, 1, 8, 12)):
        student_number, student_name = row[:2]
        activity_title, involvement = row[-2:]
        activity_date = date.fromisoformat(row[2][:10])

        activity_title = re.sub(r"^\d{8}_", "", activity_title)
        activity_title = re.sub("[-_]工作人员$", "", activity_title)
        if activity_title == "" or activity_title == "四院联谊":
            continue
        if activity_title.startswith("川兮归海"):
            activity_title = "川兮归海：新征程下的取舍与选择"
        elif activity_title == "Clound Computing":
            activity_title = "On Optimal Partitioning and Scheduling of DNNs in Mobile Edge/Cloud Computing"
        elif activity_title == "新型网络诈骗形式与预防方法":
            activity_title = "国家网络安全宣传周-网络安全专题讲座"
        elif activity_title == "高校师生同上一堂网络安全课":
            activity_title = "国家网络安全宣传周-高校师生同上一堂网络安全课"
        elif activity_title == "江苏省网络安全宣传周校园日直播活动":
            activity_title = "国家网络安全宣传周-校园日直播活动"
        elif activity_title == "图算法与及其学习的交互":
            activity_title = "图算法与机器学习的交互"
        elif activity_title == "直面国家重大卡脖子难题":
            activity_title = "直面国家重大“卡脖子”难题，投身大型工业软件自主研发的奋斗实践"
        elif activity_title == "公考讲堂":
            activity_title = "苏州中政公考讲座"
        elif "公考讲堂" in activity_title:
            activity_title = "苏州中政公考讲座"
        elif activity_title == "国家网络安全宣传周-校园日直播活动":
            activity_date = date(2022, 9, 6)
        elif activity_title == "国家网络安全宣传周-网络安全专题讲座":
            activity_date = date(2022, 9, 7)
        elif activity_title == "国家网络安全宣传周-高校师生同上一堂网络安全课":
            activity_date = date(2022, 9, 12)
        elif activity_title == "移动群智感知的室内定位与地图构建技术研究":
            activity_date = date(2022, 10, 17)

        data_detail.append([student_number, student_name, activity_title,
                            activity_date.isoformat(), involvement])

    save(filename, data_count, data_detail)

    filename = "研会活动_{}.xls".format(datetime.today().strftime("%Y%m%d"))
    book = xlrd.open_workbook(os.path.join(download_directory, filename))
    data_count = list(extract(book, "记录统计", (0, 1, 2)))
    data_detail = []
    for row in extract(book, "记录明细", (0, 2, 1, 8, 12)):
        student_number, student_name = row[:2]
        activity_title, involvement = row[-2:]
        activity_date = date.fromisoformat(row[2][:10])

        activity_title = re.sub(r"^\d{8}_", "", activity_title)
        activity_title = re.sub("[-_]工作人员$", "", activity_title)
        activity_title = re.sub("_没签退$", "", activity_title)
        if activity_title == "" or activity_title.startswith("2022缺漏次数补充"):
            continue
        elif activity_title == "第19届研究生代表大会":
            activity_title = "第十九届研究生代表大会"

        data_detail.append([student_number, student_name, activity_title,
                            activity_date.isoformat(), involvement])

    save(filename, data_count, data_detail)
