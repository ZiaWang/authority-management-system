class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class LoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """ 完成用户登陆时白名单验证、session验证、权限验证
        Args:
            request, 本次请求对象
        Return:
            None, 进入下一中间件或视图函数
            response, 响应，从当前中间件位置逐层向前返回响应给客户端
        """

        from django.shortcuts import redirect, HttpResponse
        from django.conf import settings
        from re import match

        # 白名单验证
        current_url = request.path_info
        for regex_url in settings.VALID_URLS:
            if match(pattern=regex_url, string=current_url):
                return None

        # session验证
        permission_dict = request.session.get(settings.PERMISSION_DICT)
        if not permission_dict:
            return redirect('/login/')

        # 权限验证
        flag = False
        for url in permission_dict['urls']:
            regex = f'^{url}$'
            if match(pattern=regex, string=current_url):
                request.session[settings.FEATURE_LIST] = permission_dict['features']
                flag = True
                break

        if not flag:
            return HttpResponse("你没有权限访问该操作")