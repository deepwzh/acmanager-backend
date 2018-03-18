import csv

from django.contrib.auth.models import User
from django.db.models import Sum, Count
from rest_framework import serializers

from api.models import Tongji, UserProfile

purple_book = list()
blue_book = list()
with open("api/aoapc.csv", encoding="gbk") as f:
    print("Hello?")
    csv_reader = csv.reader(f)
    flag = None
    for r in csv_reader:
        if r[0] == "入门经典":
            flag = 0
        elif r[0] == "训练指南":
            flag = 1
        elif str(r[0]).isnumeric():
            if flag == 0:
                purple_book.append(r[0])
            elif flag == 1:
                blue_book.append(r[0])

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'realName', 'type']


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class TongjiSerializer(serializers.ModelSerializer):
    count = serializers.JSONField(write_only=True)
    class Meta:
        model = UserProfile
        fields = ['username', 'realName', 'count']


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tongji = Tongji.objects.filter(user__username=instance.username)
        aoapc_data = []
        duplicate_problems = list(set(purple_book) & set(blue_book))
        purple_book_count = tongji.filter(oj_name="UVA", problem_id__in=purple_book).count()
        blue_book_count = tongji.filter(oj_name="UVA", problem_id__in=blue_book[0:1000]).count()
        blue_book_count += tongji.filter(oj_name="UVA", problem_id__in=blue_book[1000:]).count()
        duplicate_count = tongji.filter(oj_name="UVA", problem_id__in=duplicate_problems).count()
        # purple_book_count = 0
        ret['count'] = {key:value for (key, value) in tongji.values('oj_name').annotate(count=Count('problem_id'))}
        ret['count']["总数"] = tongji.count()
        ret['count']["紫书+蓝书"] = purple_book_count + blue_book_count - duplicate_count
        ret['count']["紫书"] = purple_book_count
        ret['count']["蓝书"] = blue_book_count
        return ret

    def update(self, instance, validated_data):
        pass

class AllSolvedSerializer(object):
    def __init__(self, username):
        self.username = username

    @property
    def data(self):
        res = dict()
        res["user"] = self.username
        res["data"] = dict()
        res["data"]["ojs"] = list()
        res["total"] = 0
        total = 0
        oj_names = Tongji.objects.filter(user=self.username).values("oj_name").distinct()#取出所有的oj_name且去重复
        for oj_name in oj_names:
            tongji = Tongji.objects.filter(user__username=self.username,oj_name=oj_name['oj_name']).values("problem_id")
            problemList = list()
            for i in tongji:
                problemList.append(i['problem_id'])
            res["data"]["ojs"].append({'oj_name': oj_name['oj_name'], 'total': len(problemList), 'solved': problemList})
            total += len(problemList)
        res["total"] = total
        return res

class AOAPCSolvedSerializer(object):
    def __init__(self, username):
        self.username = username
    @property
    def data(self):
        res = dict()
        res["user"] = self.username
        res["data"] = dict()
        res["data"]["ojs"] = list()
        total = 0
        aoapc_book = ProblemsSerializer().data
        tongji = Tongji.objects.filter(user__username=self.username,oj_name="UVA")
        total1 = 0
        books = ["aoapc", "aoapc_guide"]
        books_desc = ["入门经典", "训练指南"]
        unique_problems = set()
        for i in range(len(books)):
            total0 = 0
            chaps = list()
            for k, v in aoapc_book[books[i]].items():
                chap_list = v
                exist_list = list()
                cnt = 0
                for problem in chap_list:
                    if tongji.filter(problem_id=problem).exists():
                        exist_list.append(problem)
                        cnt = cnt + 1
                        unique_problems.add(problem)
                chaps.append({ 'chap': k, 'chap_desc_name': '','solved_cnt': cnt, 'solved': exist_list})
                # res["data"]["aoapc"] = res["data"]["aoapc"] +
                total0 = total0 + cnt
                total = total + cnt
            res["data"]["ojs"].append({'oj_name': books[i], 'oj_desc_name': books_desc[i], 'total': total0, 'chaps': chaps})
        res["total"] = len(unique_problems)
        return res


class ProblemsSerializer(object):
    def __init__(self):
        pass

    @property
    def data(self):
        aoapc_book = dict()
        with open("api/aoapc.csv", encoding="gbk") as f:
            csv_reader = csv.reader(f)
            flag = None
            chap = None
            for r in csv_reader:
                if r[0] == "入门经典":
                    aoapc_book["aoapc"] = dict()
                    flag = 0
                    chap = 3 - 1
                elif r[0] == "训练指南":
                    aoapc_book["aoapc_guide"] = dict()
                    flag = 1
                    chap = 0
                elif str(r[0]).startswith("C"):
                    chap = chap + 1
                    if flag == 0:
                        aoapc_book["aoapc"]["chap_" + str(chap)] = list()
                    else:
                        aoapc_book["aoapc_guide"]["chap_" + str(chap)] = list()

                elif str(r[0]).isnumeric():
                    if flag == 0:
                        aoapc_book["aoapc"]["chap_" + str(chap)].append(r[0])
                    elif flag == 1:
                        aoapc_book["aoapc_guide"]["chap_" + str(chap)].append(r[0])
        return aoapc_book

class UserACSerializer(object):

    def __init__(self, instance):
        self.instance = instance

    @property
    def data(self):
        ret = dict()
        ret["ac"] = dict()
        instance = self.instance
        tongjis = Tongji.objects.filter(user__username=instance.username)
        aoapc_data = []
        purple_book_ac = Tongji.objects.filter(user__username=instance.username, oj_name="UVA", problem_id__in=purple_book)
        blue_book_ac1 = Tongji.objects.filter(user__username=instance.username, oj_name="UVA", problem_id__in=blue_book[0:1000])
        blue_book_ac2 = Tongji.objects.filter(user__username=instance.username, oj_name="UVA", problem_id__in=blue_book[1000:])
        # purple_book_count = 0
        blue_book_count = 0
        ret["ac"]['blue_book'] = []
        ret["ac"]['purple_book'] = []
        for ac in purple_book_ac:
            ret["ac"]['purple_book'].append(ac.problem_id)
        for ac in blue_book_ac1:
            ret["ac"]['blue_book'].append(ac.problem_id)
        for ac in blue_book_ac2:
            ret["ac"]['blue_book'].append(ac.problem_id)
        for tongji in tongjis:
            ret["ac"][tongji.oj_name] = ret["ac"].get(tongji.oj_name,[]) + [tongji.problem_id]
        return ret


class RankingSerializer(object):
    def __init__(self, oj_name=None):
        self.oj_name = oj_name

    @property
    def data(self):
        res = []
        oj_name = self.oj_name
        if oj_name:
            items = Tongji.objects.filter(oj_name=self.oj_name).values('user__username','user__realName').annotate(count=Count('problem_id'))
        else:
            oj_name = '全部'
            items = Tongji.objects.values('user__username', 'user__realName').annotate(count=Count('problem_id'))
        for item in items:
            res.append(
                {'username': item['user__username'], 'realName': item['user__realName'], 'count': item['count']})

        return {
                'rankings':
                    sorted(res, key=lambda k:k['count'], reverse=True),
                'oj': {'oj_name': oj_name}}

class AoapcRankSerializer(object):
    def __init__(self):
        pass

    def union_list(self, list1, list2):
        """
        链表的合并算法，竟然需要在这里用到这个数据结构的知识，hhhhhh
        :return:
        """
        pos1 = 0
        pos2 = 0
        res = []
        while pos1 < len(list1) and pos2 < len(list2):
            if list1[pos1]['user__username'] == list2[pos2]['user__username']:
                res.append({'username':list2[pos2]['user__username'], 'realName': list2[pos2]['user__realName'], 'count': list1[pos1]['count'] + list2[pos2]['count']})
                pos1 = pos1 + 1
                pos2 = pos2 + 1
            elif list1[pos1]['user__username'] < list2[pos2]['user__username']:
                res.append({'username':list1[pos1]['user__username'], 'realName': list1[pos1]['user__realName'], 'count': list1[pos1]['count']})
                pos1 = pos1 + 1
            elif list1[pos1]['user__username'] > list2[pos2]['user__username']:
                res.append({'username':list2[pos2]['user__username'], 'realName': list2[pos2]['user__realName'], 'count': list2[pos2]['count']})
                pos2 = pos2 + 1
        while pos1 < len(list1):
            res.append({'username': list1[pos1]['user__username'], 'realName': list1[pos1]['user__realName'],
                        'count': list1[pos1]['count']})
            pos1 = pos1 + 1
        while pos2 < len(list2):
            res.append({'username': list2[pos2]['user__username'], 'realName': list2[pos2]['user__realName'],
                        'count': list2[pos2]['count']})
            pos2 = pos2 + 1
        return res

    @property
    def data(self):
        tongji = Tongji.objects.filter(oj_name="UVA")
        aoapc_data = []
        duplicate_problems = list(set(purple_book) & set(blue_book))
        problems = list(set(purple_book) | set(blue_book))
        #
        purple_book_set1 = tongji.filter(problem_id__in=problems[0:800]).\
            values('user__username',
            'user__realName').order_by('user__username').annotate(count=Count('problem_id')) # 紫书题数集合
        purple_book_set2 = tongji.filter(problem_id__in=problems[800:]).\
            values('user__username',
            'user__realName').order_by('user__username').annotate(count=Count('problem_id')) # 紫书题数集合
        return {'rankings': sorted(self.union_list(list(purple_book_set1),list(purple_book_set2)), key=lambda x:x['count'], reverse=True),
                'oj': {'oj_name':'入门经典+训练指南'}}
        # blue_book_count = tongji.filter(oj_name="UVA", problem_id__in=blue_book[0:1000]).count()
        # blue_book_count += tongji.filter(oj_name="UVA", problem_id__in=blue_book[1000:]).count()
        # duplicate_count = tongji.filter(oj_name="UVA", problem_id__in=duplicate_problems).count()
        # # purple_book_count = 0
        # ret['count'] = {key:value for (key, value) in tongji.values('oj_name').annotate(count=Count('problem_id'))}
        # ret['count']["总数"] = tongji.count()
        # ret['count']["紫书+蓝书"] = purple_book_count + blue_book_count - duplicate_count
        # ret['count']["紫书"] = purple_book_count
        # ret['count']["蓝书"] = blue_book_count
