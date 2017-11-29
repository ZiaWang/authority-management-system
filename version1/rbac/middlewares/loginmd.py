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


class LoginMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        """ 对客户端请求进行session验证
        Args:
            request, 请求对象
        Return：
            1. None, 退出当前中间件，进入下一个中间件或视图函数
            2. response响应对象, 不在继续下面的中间件或视图函数，而是将response直接返回给上一个中间件或WSGI
        """

        from django.conf import settings
        from django.shortcuts import redirect, HttpResponse
        import re

        # 验证url是否在白名单中
        current_url = request.path_info
        for url_regex in settings.VALID_URLS:
            if re.match(url_regex, current_url):
                return None

        # 验证session
        permission_dict = request.session.get(settings.PERMISSION_DICT)
        if not permission_dict:
            return redirect(to='/login/')

        # 验证权限
        flag = False
        for url in permission_dict['urls']:
            regex = f'^{url}$'
            if re.match(pattern=regex, string=current_url):
                flag = True
                break

        # 此处不return是为了存放其他逻辑

        if not flag:
            return HttpResponse('你没有该请求权限')
