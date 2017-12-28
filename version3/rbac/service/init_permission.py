from django.conf import settings
from re import match

from rbac import models


def init_permission(user, request):
    """ 初始化用户权限数据包括权限数据和与权限相关的菜单数据
    Args:
        user: 当前登陆并验证成功的用户
        request: 当前请求对象
    Return:
        None
    """

    permissions = user.roles.values("permissions__url",
                                    "permissions__feature",
                                    "permissions__id",
                                    "permissions__group_menu",
                                    "permissions__group__menu__id",
                                    "permissions__group__menu__title")

    # 权限相关
    permission_dict = {"features": [], "urls": []}
    for item in permissions:
        permission_dict["features"].append(item["permissions__feature"])
        permission_dict["urls"].append(item["permissions__url"])
    request.session[settings.PERMISSION_DICT] = permission_dict

    # 菜单相关
    menu_list = []
    for item in permissions:
        temp = {}
        temp["id"] = item["permissions__id"]
        temp["url"] = item["permissions__url"]
        temp["feature"] = item["permissions__feature"]
        temp["group_menu"] = item["permissions__group_menu"]
        temp["menu_id"] = item["permissions__group__menu__id"]
        temp["menu_title"] = item["permissions__group__menu__title"]
        menu_list.append(temp)
    request.session[settings.MENU_LIST] = menu_list



'''
    print(menu_list)
[
    {'id': 1, 'url': '/listBooks/', 'feature': 'listBooks', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 2, 'url': '/addBook/', 'feature': 'addBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 3, 'url': '/editBook/(\\d+)/', 'feature': 'editBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 4, 'url': '/delBook/(\\d+)/', 'feature': 'delBook', 'group_menu': 1, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 5, 'url': '/listOrders/', 'feature': 'listOrders', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 6, 'url': '/addOrder/', 'feature': 'addOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 7, 'url': '/delOrder/(\\d+)/', 'feature': 'delOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 8, 'url': '/editOrder/(\\d+)/', 'feature': 'editOrder', 'group_menu': 5, 'menu_id': 1, 'menu_title': '管理菜单'}, 
    {'id': 9, 'url': '/home/', 'feature': 'home', 'group_menu': None, 'menu_id': 2, 'menu_title': '导航菜单'}]

'''
