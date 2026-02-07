"""
自定义异常层级
"""


class VibeBlogError(Exception):
    """基础异常"""
    status_code = 500

    def __init__(self, message='内部服务错误', status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(VibeBlogError):
    """请求参数验证错误 (400)"""
    status_code = 400

    def __init__(self, message='请求参数无效'):
        super().__init__(message, 400)


class NotFoundError(VibeBlogError):
    """资源不存在 (404)"""
    status_code = 404

    def __init__(self, message='资源不存在'):
        super().__init__(message, 404)


class ServiceUnavailableError(VibeBlogError):
    """服务不可用 (503)"""
    status_code = 503

    def __init__(self, message='服务暂时不可用'):
        super().__init__(message, 503)
