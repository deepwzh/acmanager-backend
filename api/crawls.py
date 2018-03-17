import json
import threading
import re
import requests
import time
from requests.exceptions import ConnectionError
from django.db import OperationalError
from rest_framework import status
from rest_framework.exceptions import NotFound, APIException

from api.exceptions import ServiceUnavailable
from api.models import Tongji
from api.models import UserProfile

def get_poj_problems(url):
    """
    抓取poj的Solved Problems List
    return: problems列表
    """
    res = requests.get(url)
    string=res.text
    pattern=r'(?<=p\()[0-9]{4}(?=\))'
    matchObj=re.finditer(pattern,string)
    problemList=[]
    for it in matchObj:
        problemList.append(it.group())
    return problemList


def get_json_data(url, n=2):
    """
    请求指定url，获取json文件
    :param url:
    :param n: 请求重试次数
    :return: 返回一个dict对象
    """
    cnt = 0
    while cnt < n:
        try:
            u = requests.get(url)
            data = json.loads(u.text)
            return data
        except (ConnectionAbortedError, ConnectionError):
            time.sleep(1)
            print("error")
            cnt = cnt + 1

    raise APIException(detail="网络异常，请检查服务器外网连接情况", code=status.HTTP_503_SERVICE_UNAVAILABLE)


def get_number_dict():
    """
    获取UVA题号与序号的对应关系，详情见[https://uhunt.onlinejudge.org/api](https://uhunt.onlinejudge.org/api)
    的api/p部分
    :return:
    """
    id_to_number = dict()
    # json.loads(u.text)
    with open("api/p.json", 'r', encoding="utf-8") as f:
        items = json.load(f)
    for item in items:
        id_to_number[item[0]] = item[1]
    return id_to_number


def getUserAcList(username):
    """
    获取指定用户的AC题目数据
    :param username: 用户名
    :return:
    """
    id_to_number = get_number_dict()
    user = UserProfile.objects.get(username=username)
    # print(user.vjname)
    vj_url = None
    uva_url = None
    poj_url = None
    # 从vj抓取题目
    vj_url = "https://cn.vjudge.net/user/solveDetail/%s" % user.vjname
    data = get_json_data(vj_url)
    # with open("main/data.json", "r") as f:
    #     data = json.load(f)
    vjRecords = data["acRecords"]
    while True:
        try:
            raw_tongjis = Tongji.objects.filter(user=user)
            break
        except OperationalError:
            time.sleep(1)

    exist_tongjis = set()
    for tongji in raw_tongjis:
        exist_tongjis.add(tongji.oj_name + "#" + tongji.problem_id)
    tongjis = set()
    for key in vjRecords:
        for problem in vjRecords[key]:
            # record = Tongji(user=user, oj_name=key, problem_id=problem)
            tongjis.add(str(key + "#" + problem))

    # 从uva抓取题目###########################################
    uva_url = "https://uhunt.onlinejudge.org/api/subs-user/%s" % user.uvaId
    uvaRecords = get_json_data(uva_url)
    uva_ac_sets = set()
    for record in uvaRecords["subs"]:
        if record[2] == 90:
            tongjis.add(str("UVA" + "#" + str(id_to_number[record[1]])))

    # 从poj抓取题目###########################################
    poj_url = "http://poj.org/userstatus?user_id=%s" % user.pojName
    poj_problems = get_poj_problems(poj_url)
    #poj_ac_sets = set()
    for poj_problem in poj_problems:
        tongjis.add(str("POJ" + "#" + poj_problem))
    records = []
    for item in tongjis - exist_tongjis:
        oj_name, problem_id = str(item).split("#")
        records.append(Tongji(user=user, oj_name=oj_name, problem_id=problem_id))

    while True:
        try:
            Tongji.objects.bulk_create(records)
            break
        except OperationalError:
            time.sleep(1)

    print("%s抓取完成" % user.username)


def get_user_ac_lists():
    """
    使用多线程抓取所有用户AC的题目
    :return:
    """
    crawl_queue = list(UserProfile.objects.all())
    threads = []

    def process_queue():
        user = crawl_queue.pop()
        print(user.type)
        print("正在抓取：" + user.username)
        getUserAcList(user.username)

    # 建立线程池
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < 10 and crawl_queue:
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
