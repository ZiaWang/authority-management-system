from django.conf import settings


def init_permission(user, request):
    """ 初始化用户权限，并将数据保存到session中
    Args:
        user: 用户对象，用来获取权限相关数据
        request: 请求对象，用来存放用户权限数据到session中
    Return:
        None
    """

    permissions = user.roles.values('permissions__url' , 'permissions__feature')
    permission_dict = {'features': [], 'urls': []}
    for item in permissions:
        permission_dict['features'].append(item['permissions__feature'])
        permission_dict['urls'].append(item['permissions__url'])

    request.session[settings.PERMISSION_DICT] = permission_dict
