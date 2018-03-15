from django.contrib.auth.models import User


class AuthBackend(object):
    """
    自定义的权限验证授权后端，规则是，密码值相同，即通过，不需要任何加密算法处理（前端已经加密过了）
    """

    def authenticate(self, username=None, password=None):
        """
        判断是否密码相同
        :param username: 用户名
        :param password: 密码
        :return: 如果通过权限验证，返回user对象，否则返回None
        """
        try:
            user = User.objects.get(username=username)
            if user.password == password:
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None