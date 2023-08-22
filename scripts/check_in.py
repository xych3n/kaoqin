"""
Automated script for checking in and out. Given a .txt file containing NFC serial numbers
exported by a check machine (currently HDT3000), this script requests the check system to 
download a .xls file containing corresponding student numbers.

Dependencies:
- xlwt
- selenium

Usage:
- Adjust login credentials, URLs, and other settings as needed.
- Provide input .txt file with NFC serial numbers.
- Optionally provide output .txt file for intersection comparison.
- Set the title for the activity corresponding to the input file.

Note:
- Username and password have been removed from this script for security reasons. (Line 71-72)
"""

import os
from datetime import date, datetime, time, timedelta
from typing import Optional, Sequence

import xlwt
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def txt2xls(in_filename: str, out_filename: Optional[str]) -> Sequence[str]:
    """
    NOTE: `in_` and `out_` not for input and output, but for CHECK IN and CHECK OUT!
    """
    assert in_filename.endswith(".txt")
    with open(in_filename) as f:
        uids = set([row.strip().split(maxsplit=1)[0]
                    for row in f.readlines()])
    if out_filename is not None:
        assert out_filename.endswith(".txt")
        with open(out_filename) as f:
            int_uids = set([row.strip().split(maxsplit=1)[0]
                            for row in f.readlines()])
            print("Not checked out but checked in:")
            print(*(uids - int_uids), sep="\n")
            print("Not checked in but checked out:")
            print(*(int_uids - uids), sep="\n")
            uids &= int_uids
    return sorted(uids)


def main(
    filename: str,
    intersection_filename: Optional[str],
    activity_title: str,
) -> None:
    xls_filename = filename.replace(".txt", ".xls")
    uids = txt2xls(filename, intersection_filename)
    # create driver
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"download.default_directory" : os.path.abspath(".")}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(options=options)
    # login
    driver.get("http://222.192.16.12/index.aspx")
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "usd")),
    ).send_keys("")
    driver.find_element(value="pwd").send_keys("")
    driver.find_element(value="Button1").click()
    print("Successfully loged in.")
    # query for history conferences
    driver.get("http://222.192.16.12/page/Setting/ConferenceSet.aspx")
    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "Select")),
    ).click()
    button = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "DataGrid1_ctl03_ImageButton1")),
    )
    # determine activity date, then write into xls file
    latest_date = driver.find_element(by=By.XPATH, value='//*[@id="DataGrid1"]/tbody/tr[2]/td[5]').text
    latest_date = date.fromisoformat(latest_date)
    latest_date = max(latest_date, date.today())
    activity_date = latest_date + timedelta(days=1)
    current_time = datetime.combine(activity_date, time(hour=9))
    interval = timedelta(minutes=1)
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sheet1")
    sheet.write(0, 0, "卡号")
    sheet.write(0, 1, "时间")
    for i, uid in enumerate(uids, start=1):
        sheet.write(i, 0, uid)
        current_time += interval
        sheet.write(i, 1, current_time.strftime("%Y-%m-%d %H:%M"))
    workbook.save(xls_filename)
    # add conference
    button.click()
    element = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "txtConferenceName")),
    )
    element.clear()
    element.send_keys(activity_title)
    element = driver.find_element(value="txtConferenceDate")
    driver.execute_script("arguments[0].removeAttribute('readonly')", element)
    element.clear()
    element.send_keys(activity_date.strftime("%Y-%m-%d"))
    driver.find_element(value="cmbBoardRoomID").click()
    driver.find_element(value="Insert").click()
    try:
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.ID, "Label1"), "插入成功"),
        )
    except TimeoutException:
        message = driver.find_element(value="Label1").text
        print(message)
        raise
    print("Successfully added conference.")
    # add participants
    driver.get("http://222.192.16.12/page/Setting/conferenceWaterListImport.aspx")
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.ID, "excelfile")),
    ).send_keys(os.path.abspath(xls_filename))
    driver.find_element(value="btnSeeData").click()
    element = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "ddlConference")),
    )
    element.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
    element = driver.find_element(value="ddlWaterType")
    element.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
    driver.find_element(value="btnImport").click()
    WebDriverWait(driver, 2).until(
        EC.text_to_be_present_in_element((By.ID, "LinkButton1"), "查看结果"),
    )
    print("Successfully added participants.")
    # download results after conversion
    driver.get("http://222.192.16.12//page/Settlement/MeetingSelect.aspx")
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.ID, "Select")),
    ).click()
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.ID, "toExcel")),
    ).click()
    # wait for downloading, then rename the file
    outfile = "E___________Web_page_Settlement_{}.xls".format(
        datetime.today().strftime("%Y-%m-%d"),
    )
    while True:
        if os.path.exists(outfile):
            os.rename(outfile, "{}_签到表.xls".format(activity_title))
            break
    driver.close()
    print("Successfully downloaded file.")
