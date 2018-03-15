from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'