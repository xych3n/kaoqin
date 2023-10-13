"""
How to package:
    pyinstaller daka.py --clean
"""

import os
import re
from datetime import date, datetime, time, timedelta
from sys import argv, exit
from tempfile import TemporaryFile
from tkinter.messagebox import showerror, showinfo

from requests import session
from xlrd import open_workbook
from xlwt import Workbook


if __name__ == "__main__":
    # read file(s), and get activity title and uids
    filenames = argv[1:]
    if len(filenames) == 0:
        showerror("", "需至少选择一个文件")
        exit()
    title = None
    uids_in = None
    uids_out = None
    for filename in filenames:
        if not os.path.exists(filename):
            showerror("", "路径{!r}所指向的文件不存在".format(filename))
            exit()
        basename = os.path.basename(filename)
        if not basename.endswith(".txt"):
            showerror("", "仅支持.txt文件")
            exit()
        m = re.match(r"(.+?)_(in|out)\d*.txt", basename)
        if m is None:
            showerror("", "文件名{!r}格式错误".format(filename))
            exit()
        title_field, type_field = m.groups()
        if title is None:
            title = title_field
        elif title != title_field:
            showerror("", "活动名称需保持一致")
            exit()
        with open(filename) as f:
            for line in f:
                try:
                    uid = line.split(maxsplit=1)[0]
                except IndexError:
                    continue
                if not uid.isdigit():
                    continue
                if type_field == "in":
                    if uids_in is None:
                        uids_in = set()
                    uids_in.add(uid)
                else:
                    if uids_out is None:
                        uids_out = set()
                    uids_out.add(uid)
    if uids_in is None:
        showerror("", "需至少包含一份签到文件")
        exit()
    if uids_out is not None:
        uids = uids_in & uids_out
    else:
        uids = uids_in
    uids = sorted(uids)
    assert title is not None
    title = "{}_{}".format(date.today().strftime("%Y%m%d"), title)
    # login
    s = session()
    r = s.get("http://222.192.16.12/page/login.aspx?ReturnUrl=../index.aspx")
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取ViewState失败".format("login.aspx"))
        exit()
    __VIEWSTATE = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "LoginType": "学工号:".encode("GB18030"),
        "usd": "07D021",
        "pwd": "113542",
        "Button1.x": 29,    # any number is ok
        "Button1.y": 13,    # any number is ok
    }
    r = s.post("http://222.192.16.12/page/login.aspx?ReturnUrl=../index.aspx",
               data=data, allow_redirects=False)
    if r.cookies.get("administrator") is None:
        showerror("", "登录失败")
        exit()
    # request the latest conference, and determine the date of the activity to be added
    r = s.get("http://222.192.16.12/page/Setting/ConferenceSet.aspx")
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取ViewState失败".format("ConferenceSet.aspx"))
        exit()
    __VIEWSTATE = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "Select": "查 询".encode("GB18030"),
    }
    r = s.post("http://222.192.16.12/page/Setting/ConferenceSet.aspx", data=data)
    m = re.search(r'(?s)id="DataGrid1_ctl\d*_Linkbutton2".*?</td>.*?(\d\d\d\d-\d\d-\d\d)', r.text)
    if m is None:
        showerror("", "解析最近的一次活动失败")
        exit()
    latest_date = m.group(1)
    latest_date = date.fromisoformat(latest_date)
    conference_date = max(latest_date, date.today()) + timedelta(days=1)
    # write data to temporary file in xls format
    workbook = Workbook()
    sheet = workbook.add_sheet("Sheet1")
    sheet.write(0, 0, "卡号")
    sheet.write(0, 1, "时间")
    current_time = datetime.combine(conference_date, time(hour=8))
    interval = timedelta(minutes=1)
    for i, uid in enumerate(uids, start=1):
        sheet.write(i, 0, uid)
        current_time += interval
        sheet.write(i, 1, current_time.strftime("%Y-%m-%d %H:%M"))
    fp = TemporaryFile(suffix=".xls")
    workbook.save(fp)
    # add conference
    r = s.get("http://222.192.16.12/page/Setting/ConferenceAdd.aspx")
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取ViewState失败".format("ConferenceAdd.aspx"))
        exit()
    __VIEWSTATE = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "DpConferenceType": 1,
        "txtConferenceName": title.encode("GB18030"),
        "txtNodes": "",
        "remLen": 50,
        "txtConferenceDate": conference_date.isoformat(),
        "txtConferencedays": 1,
        "txtOnstartTime": "08:00",
        "txtOnEndTime": "20:00",
        "txtAttendNum": 500,
        "cmbBoardRoomID": 29,
        "DepartName": "技术学院".encode("GB18030"),
        "DBTNumber": 0,
        "cmbAttendenceType": 2,
        "SelectDepartment1$DepartName": "请选择参会部门".encode("GB18030"),
        "SelectDepartment1$DepartID": "000",
        "SelectDepartment1$ParentID": "000",
        "Insert": " 添加 ".encode("GB18030"),
        "DepartID": "001212",
        "ParentID": "",
        "dbtCount": 0,
    }
    r = s.post("http://222.192.16.12/page/Setting/ConferenceAdd.aspx", data=data)
    m = re.search('<span id="Label1"><font color="#FF3333">(.*?)</font>', r.text)
    if m is None:
        showerror("", "解析插入会议结果失败")
        exit()
    if m.group(1) != "插入成功":
        showerror("", "添加会议失败")
        exit()
    # upload temporary file
    r = s.get("http://222.192.16.12/page/Setting/conferenceWaterListImport.aspx")
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取ViewState失败".format("conferenceWaterListImport.aspx"))
        exit()
    __VIEWSTATE = m.group(1)
    m = re.search('id="__EVENTVALIDATION" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取EventValidation失败".format("conferenceWaterListImport.aspx"))
        exit()
    __EVENTVALIDATION = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "__EVENTVALIDATION": __EVENTVALIDATION,
        "btnSeeData": "查看".encode("GB18030"),
    }
    fp.seek(0)
    files = {"excelfile": fp}
    r = s.post("http://222.192.16.12/page/Setting/conferenceWaterListImport.aspx",
               data=data, files=files)
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    assert m is not None
    __VIEWSTATE = m.group(1)
    m = re.search('id="__EVENTVALIDATION" value="(.*?)"', r.text)
    assert m is not None
    __EVENTVALIDATION = m.group(1)
    m = re.search(r'option value="(\d+)"', r.text)
    assert m is not None
    ddlConference = m.group(1)
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": __VIEWSTATE,
        "__EVENTVALIDATION": __EVENTVALIDATION,
        "WorkAreaID": "",
        "dlSheet": "Sheet1",
        "ddlConference": ddlConference,
        "ddlWaterType": 208,
        "btnImport": "导入数据库".encode("GB18030"),
        "hidfile": fp.name,
    }
    r = s.post("http://222.192.16.12/page/Setting/conferenceWaterListImport.aspx",
               data=data, files=files)
    # download the uploading result
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取ViewState失败".format("conferenceWaterListImport.aspx"))
        exit()
    __VIEWSTATE = m.group(1)
    m = re.search('id="__EVENTVALIDATION" value="(.*?)"', r.text)
    if m is None:
        showerror("", "在访问{}时获取EventValidation失败".format("conferenceWaterListImport.aspx"))
        exit()
    __EVENTVALIDATION = m.group(1)
    data = {
        "__EVENTTARGET": "LinkButton1",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": __VIEWSTATE,
        "__EVENTVALIDATION": __EVENTVALIDATION,
        "WorkAreaID": "",
        "dlSheet": "Sheet1",
        "ddlConference": ddlConference,
        "ddlWaterType": 208,
        "hidfile": fp.name,
    }
    r = s.post("http://222.192.16.12/page/Setting/conferenceWaterListImport.aspx",
               data=data, files=files, stream=True)
    fp.close()
    with open("会议考勤流水批量导入结果.txt", "wb") as f:
        for chunk in r.iter_content(chunk_size=None):
            f.write(chunk)
    # download the .xls file
    r = s.get("http://222.192.16.12//page/Settlement/MeetingSelect.aspx")
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    assert m is not None
    __VIEWSTATE = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "Select": "查询",
        "MeetName": ddlConference,
    }
    r = s.post("http://222.192.16.12//page/Settlement/MeetingSelect.aspx", data=data)
    m = re.search('id="__VIEWSTATE" value="(.*?)"', r.text)
    assert m is not None
    __VIEWSTATE = m.group(1)
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "toExcel": "输出到Excel".encode("GB18030"),
        "MeetName": ddlConference,
    }
    r = s.post("http://222.192.16.12//page/Settlement/MeetingSelect.aspx", data=data, stream=True)
    fp = TemporaryFile(suffix=".xls")
    for chunk in r.iter_content(chunk_size=None):
        fp.write(chunk)
    fp.seek(0)
    workbook = open_workbook(file_contents=fp.read())
    fp.close()
    sheet = workbook.sheet_by_name(workbook.sheet_names()[0])
    data = []
    for i in range(1, sheet.nrows):
        student_number = sheet.cell_value(i, 0)
        name = sheet.cell_value(i, 1).strip()
        check_time = sheet.cell_value(i, 10)
        data.append((student_number, name, check_time))
    data.sort(key=lambda x: x[2])
    workbook = Workbook()
    sheet = workbook.add_sheet("Sheet1")
    sheet.write(0, 0, "学号")
    sheet.write(0, 1, "姓名")
    for i, (student_number, name, _) in enumerate(data, start=1):
        sheet.write(i, 0, student_number)
        sheet.write(i, 1, name)
    workbook.save("{}_签到表.xls".format(title))
    showinfo("", "导入成功")
