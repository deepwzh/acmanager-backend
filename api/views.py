from MySQLdb.cursors import DictCursor
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import config
from api.crawls import getUserAcList, get_user_ac_lists
from api.models import UserProfile
from api.serializers import TongjiSerializer, UserACSerializer, ProblemsSerializer, AOAPCSolvedSerializer, \
    RankingSerializer, AoapcRankSerializer, UserProfileSerializer, UserLoginSerializer, AllSolvedSerializer
import MySQLdb


# class Tongji(APIView):
#
#     def get(self, request):
#         users = UserProfile.objects.all()
#         serializer = TongjiSerializer(users, many=True)
#
#         return Response({'ac': serializer.data, 'ojs':['总数', '紫书+蓝书', '紫书' ,'蓝书', 'UVA', 'UVALive','51Nod', 'CodeForces', 'FZU', 'Gym', 'HDU',#}
#             'HYSBZ', 'LightOJ',  'OpenJ_POJ', 'POJ', 'SGU', 'URAL', 'ZOJ']}, status=status.HTTP_200_OK)


class UserAC(APIView):
    def get(self, request, **kwargs):
        # if request.GET['username']:
        username = kwargs.get("username", None)
        try:
            if username is None:
                raise UserProfile.DoesNotExist
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户名不存在"}, status=status.HTTP_200_OK)
        serializer = UserACSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SyncUser(APIView):
    def get(self, request):
        conn = MySQLdb.connect(**config.old_acmanager_db_config)
        cur = conn.cursor(cursorclass=DictCursor)
        cur.execute("select `username`, `password`, `realName`, `major`,"
                    " `type`, `uvaId`, `vjname`, `hduName`, `pojName`  from `user`")
        data = cur.fetchall()
        User.objects.filter(is_staff=False).delete()
        UserProfile.objects.all().delete()
        users = []
        for user in data:
            base_user = User(username=user["username"], password=user["password"])
            base_user.save()
            users.append(UserProfile(user=base_user, username=user["username"], realName=user["realName"], pojName=user["pojName"], uvaId=user["uvaId"], vjname=user["vjname"], type=user['type']))
            print(user['username'])
        UserProfile.objects.bulk_create(users)
        cur.close()
        return Response({"message" : "用户同步成功"}, status=status.HTTP_200_OK)


class Solved(object):
    class AOAPCSolvedView(APIView):
        def get(self, request, username):
            serializer = AOAPCSolvedSerializer(username)
            return Response(serializer.data, status=status.HTTP_200_OK)

    class SolvedView(APIView):
        def get(self, request):
            pass

    class AllSolvedView(APIView):
        def get(self, request, username):
            serializer = AllSolvedSerializer(username)
            return Response(serializer.data, status=status.HTTP_200_OK)

class Problems(object):
    class AOAPCProblemView(APIView):
        def get(self, request):
            serializer = ProblemsSerializer()
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)


class Rankings(object):
    class RankingView(APIView):
        def get(self, request):
            serializer = RankingSerializer()
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    class RankingDetailView(APIView):
        def get(self, request, oj_name):
            if oj_name == "aoapc":
                serializer = AoapcRankSerializer()
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                serializer = RankingSerializer(oj_name)
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class SessionView(APIView):
    """
    查询用户登录状态API
    """
    def get(self, request):
        print(request.user)
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class LoginView(APIView):
    """
    用户登陆API
    """
    def post(self, request):
        #Access-Control-Allow-Origin
        # headers={'Access-Control-Allow-Credentials':'true', 'Access-Control-Allow-Origin':'http://127.0.0.1:4444'}
        print(request.data)
        if request.user.username != "":
            print(request.user)
            message = "您已经登录，不要重复登录"
            return Response({'message': message})
        username = ""
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if user:
            login(request, user)
            username = user.username
            message = "登录成功"
            print(request.user)
            return Response({'message': message, 'username': username})
        else:
            message = "登录失败，请检查用户名或密码"
            return Response({'message': message})


class LogoutAPIView(APIView):
    """
    用户注销API
    """
    def get(self, request):
        logout(request)
        return Response({'message': 'success'})


class StatisticsNumberUpdateView(APIView):
    def get(self, request, **kwargs):
        if kwargs.get("username"):
            getUserAcList(kwargs.get("username"))
        else:
            get_user_ac_lists()
        print(kwargs.get('username'))
        return HttpResponse({'message': 'success'})
