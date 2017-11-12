from django.conf import settings


def init_permission(user, request):
    """ 初始化用户权限，并将数据保存到session中
        参数:
            user: 用户对象
            request: 请求对象
        返回值: None
    """
    permissions = user.roles.values('permissions__url' , 'permissions__feature')
    permission_dict = {'features': [], 'urls': []}
    for item in permissions:
        permission_dict['features'].append(item['permissions__feature'])
        permission_dict['urls'].append(item['permissions__url'])

    request.session[settings.FEATURE_LIST] = permission_dict['features']
    request.session[settings.PERMISSION_DICT] = permission_dict
