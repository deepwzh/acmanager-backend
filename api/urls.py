from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.views.decorators.cache import cache_page

from api import views
from api.views import SyncUser, UserAC, Problems, Solved, Rankings, SessionView, LoginView, LogoutAPIView

"""
AC题目数列表
AC题目详情
UVA AC题目数详情
uva
api/ac list-查看所有用户的AC题数
        detail-查看该用户的AC详细
api/ac/uva list-查看所有用户的UVA各单元AC题数
        detail-查看该用户UVA的AC详细

"""
urlpatterns = [
    # url(r'ac$', cache_page(60*15)(Tongji.as_view()), name="api-ac-list"),
    # url(r'ac/users/(?P<username>.*)$', UserAC.as_view(), name="api-ac-user-detail"),
    # url(r'ac/users/(?P<username>.*)$', UserAC.as_view(), name="api-ac-user-detail"),
    # 同步用户
    url(r'users/sync$', SyncUser.as_view(), name='api-sync-user'),
    # 入门经典+训练指南题目列表
    url(r'problems/uva$', Problems.AOAPCProblemView.as_view()),
    # 用户解决题目一览
    url(r'users/(?P<username>.*)/solved/uva', Solved.AOAPCSolvedView.as_view()),  # 用户入门经典+训练指南题数详细统计
    url(r'users/(?P<username>.*)/solved/all', Solved.AllSolvedView.as_view()), #用户解决题数统计
    url(r'users/(?P<username>.*)/solved$', Solved.SolvedView.as_view()),  # 用户汇总题数统计
    # 用户题数排名
    url(r'rankings/(?P<oj_name>.*)$', Rankings.RankingDetailView.as_view()),  # 用户单个OJ题数排名
    url(r'rankings$', Rankings.RankingView.as_view()), # 用户总题数排名
    # url(r'users/profile$', SyncUser.as_view()),
    # 用户题数更新
    url(r'userac/update$', views.StatisticsNumberUpdateView.as_view(), name='run'),
    url(r'userac/update/(?P<username>.*)$', views.StatisticsNumberUpdateView.as_view(), name='run'),
    # 用户登陆/注销/登陆状态查询
    url(r'session$', SessionView.as_view()),
    url(r'login$', LoginView.as_view()),
    url(r'logout', LogoutAPIView.as_view())
]
