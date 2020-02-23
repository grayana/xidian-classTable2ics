import json
import re
from datetime import datetime, timedelta

timeSchedule_summer = {'1': '0830', '2': '0920', '3': '1025', '4': '1115', '5': '1430',
                       '6': '1520', '7': '1625', '8': '1715', '9': '1930', '10': '2020', '11': '2105'
                       }
timeSchedule_winter = {'1': '0830', '2': '0920', '3': '1025', '4': '1115', '5': '1400',
                       '6': '1450', '7': '1555', '8': '1645', '9': '1900', '10': '1950', '11': '2035'
                       }
termStart = '20190826'#学期开始日期
Sday = datetime.strptime(termStart, '%Y%m%d')
Summer = datetime.strptime(str(datetime.today().year) + '1001', '%Y%m%d')
Nday = (Sday + timedelta(days=7)).strftime('%Y%m%d' + 'T')


def week2num(byDay):
    dict = {
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '日': 7
    }
    return dict[byDay]


def weeksFormat(weeks):
    # 将周数范围转化为详细的周
    accuTime = {
        'week': [],
        'byDay': 0,
        'Stime': None,
        'Etime': None
    }
    if weeks:
        # 提取周的范围
        grp = re.match(r'(^[0-9/\-/,/双/单/周]+).*星期(.)*\[(\d+)-(\d+)', weeks).groups()
        week = grp[0].split(',')
        accuTime['Stime'] = grp[2]
        accuTime['Etime'] = grp[3]
        for i in week:
            step = 1
            a = re.match(r'([0-9/\-]+)', i).groups()
            if re.match('.*[单/双]', i):
                step = 2
            a = list(map(int, a[0].split('-')))
            if a.__len__() > 1:
                a = range(a[0], a[1] + 1, step)
            for j in a:
                accuTime['week'].append(j)
        accuTime['byDay'] = week2num(grp[1])
    return accuTime

#读取课表JSON数据
file = open('class.txt', 'r', encoding='utf-8')
orgin = file.read()
crouse = json.loads(orgin)
file.close()


# 删除不必要字段
for i in crouse:
    for j in list(i):
        if not re.match(r'^(?:RKJS|PKSJ|PKDD|KCMC)$', j):
            del i[j]


# 处理上课时间
for ii in crouse:
    if ii['PKSJ']:
        ii['PKSJ'] = re.split(r'\].', ii['PKSJ'])


# ICS文件格式
header = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VTIMEZONE\nTZID:China Standard Time\nBEGIN:STANDARD\nDTSTART:16010101T000000\nTZOFFSETFROM:+0800\nTZOFFSETTO:+0800\nEND:STANDARD\nEND:VTIMEZONE\n"
end = "END:VCALENDAR"


# 写入ICS文件
test = open('test.ics', 'w', encoding='utf-8')
test.write(header)
for eachClass in crouse:
    RKJS = eachClass['RKJS']
    room = eachClass['PKDD']
    KCMC = eachClass['KCMC']
    if eachClass['PKSJ']:
        for k in eachClass['PKSJ']:
            I = weeksFormat(k)
            for i in I['week']:
                delta = timedelta(days=(i - 1) * 7 + I['byDay'] - 1)
                startDay = Sday + delta
                if startDay < Summer:
                    startTime = startDay.strftime('%Y%m%d') + 'T' + timeSchedule_summer[I['Stime']] + '00'
                    endTime = startDay.strftime('%Y%m%d') + 'T' + timeSchedule_summer[I['Etime']]
                    endTime = (datetime.strptime(endTime, '%Y%m%dT%H%M') + timedelta(minutes=45)).strftime(
                        '%Y%m%dT%H%M%S')
                else:
                    startTime = startDay.strftime('%Y%m%d') + 'T' + timeSchedule_winter[I['Stime']] + '00'
                    endTime = startDay.strftime('%Y%m%d') + 'T' + timeSchedule_winter[I['Etime']]
                    endTime = (datetime.strptime(endTime, '%Y%m%dT%H%M') + timedelta(minutes=45)).strftime(
                        '%Y%m%dT%H%M%S')
                crouse_info = "BEGIN:VEVENT\n" \
                              "CLASS:PUBLIC\n" \
                              "DESCRIPTION: \\n\n" \
                              "DTEND;TZID=\"China Standard Time\":" + endTime + "\n" \
                              "DTSTART;TZID=\"China Standard Time\":" + startTime + "\n" \
                              "LOCATION:" + room + "\n""PRIORITY:5\n" + "SEQUENCE:0\n" \
                              "SUMMARY;LANGUAGE=zh-cn:" + room + "|" + KCMC + "-" + RKJS + "\n" + "TRANSP:OPAQUE\n" + "END:VEVENT\n"
                test.write(crouse_info)
test.write(end)
test.close()
