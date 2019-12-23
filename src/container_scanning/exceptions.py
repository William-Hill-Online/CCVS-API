from rest_framework.exceptions import APIException


class VendorException(APIException):
    def __init__(self, detail=None, code=None):
        return super().__init__(detail=detail, code=code)
