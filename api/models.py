from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="user_profile", on_delete=models.ForeignKey)
    username = models.CharField(max_length=20, primary_key=True)
    realName = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=20, null=True)
    vjname = models.CharField(null=True, max_length=20)
    uvaId = models.CharField(null=True, max_length=20)


class Tongji(models.Model):
    user = models.ForeignKey(UserProfile, related_name='tongji')
    oj_name = models.CharField(max_length=15)
    problem_id = models.CharField(max_length=15)

    class Meta:
        unique_together = ('user', 'oj_name', 'problem_id')