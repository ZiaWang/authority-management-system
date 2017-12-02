from django.conf import settings


def init_permission(user, request):
    """ 初始化用户权限，并将数据保存到session中(包括初始化菜单数据和用户权限数据)
    Args:
        user: 用户对象
        request: 请求对象
    Return: None
    """

    permissions = user.roles.values('permissions__url',
                                    'permissions__feature',
                                    'permissions__is_menu',
                                    'permissions__group_id',
                                    'permissions__group__menu__id',
                                    'permissions__group__menu__title'
                                    ).distinct()

    # 用户权限相关
    permission_dict = {'features': [], 'urls': []}
    for item in permissions:
        permission_dict['features'].append(item['permissions__feature'])
        permission_dict['urls'].append(item['permissions__url'])

    request.session[settings.FEATURE_LIST] = permission_dict['features']
    request.session[settings.PERMISSION_DICT] = permission_dict

    menu_list = []
    for item in permissions:
        tpl = {}
        if not item['permissions__is_menu']:
            continue
        tpl['menu_id'] = item['permissions__group__menu__id']
        tpl['menu_title'] = item['permissions__group__menu__title']
        tpl['feature'] = item['permissions__feature']
        tpl['url'] = item['permissions__url']
        tpl['active'] = False
        menu_list.append(tpl)

    request.session[settings.MENU_LIST] = menu_list
