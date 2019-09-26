#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import json
from retry import retry

header = {
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; "
                  ".NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729) "
}
curl = "http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fehall.xidian.edu.cn%2Fgsapp%2Fsys%2Fwdkbapp%2F" \
       "*default%2Findex.do%3Famp_sec_version_%3D1 "
session = requests.session()
session.headers = header


def getLT():
    """获取登陆所需的lt，execution"""
    respons = session.get(curl)
    g = re.search(r'name="lt" value="(.*?-cas).*?ue="(\w+)"', respons.text, re.S).groups()
    return g


@retry()
def login(lt):
    id = input("请输入学号：")
    pwd = input("请输入统一登陆密码：")
    data = {
        "username": id,
        "password": pwd,
        "submit": "",
        "lt": lt[0],
        "execution": lt[1],
        "_eventId": "submit",
        "rmShown": "1"
    }
    response = session.post(curl, data=data, headers=header)
    if re.search(r'err_login', response.content.decode('utf-8'), re.S):
        print('登录失败！请检查学号或密码')
        raise Exception('登录失败！请检查学号或密码')
    else:
        print('登录成功')
    return session

lt = getLT()
session = login(lt)

termUrl = 'http://ehall.xidian.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/kfdxnxqcx.do'
response = session.post(termUrl, headers=header)
term = json.loads(response.content)['datas']['kfdxnxqcx']['rows'][0]['XNXQDM']
url = "http://ehall.xidian.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/xsjxrwcx.do"
data1 = {
    "XNXQDM": term,
    "pageNumber": "1",
    "pageSize": "20"
}
response = session.post(url, data=data1, headers=header)
classtable = json.loads(response.content.decode('utf-8'))
table = classtable["datas"]["xsjxrwcx"]["rows"]
js = json.dumps(table)
file = open('class.txt', 'w', encoding='utf-8')
file.write(js)
file.close()
print('课表JSON数据已保存为class.txt')
