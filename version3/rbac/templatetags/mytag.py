from django.template import Library
from django.conf import settings
from re import match

register = Library()


@register.inclusion_tag(filename='menu.html')
def menu_html(request):
    """ 生成渲染菜单的数据结构并返回该数据
    Args:
        request: 请求对象
    """

    current_url = request.path_info
    menu_list = request.session.get(settings.MENU_LIST)

    menu_dict = {}
    for item in menu_list:
        if not item['group_menu']:
            menu_dict[item['id']] = item

    for item in menu_list:
        regex_url = f'^{item["url"]}$'
        if match(pattern=regex_url, string=current_url):
            group_menu = item['group_menu']
            if group_menu:              # 当前url关联了一个组内菜单
                menu_dict[group_menu]['active'] = True
            else:                       # 当前url是组内菜单中被关联的对象(null=True)
                menu_dict[item['id']]['active'] = True

    '''
    {
        1: {'id': 1, 'url': '/listBooks/', 'feature': 'listBooks', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}, 
        5: {'id': 5, 'url': '/listOrders/', 'feature': 'listOrders', 'group_menu': None, 'menu_id': 1, 'menu_title': '管理菜单'}, 
        9: {'id': 9, 'url': '/home/', 'feature': 'home', 'group_menu': None, 'menu_id': 2, 'menu_title': '导航菜单', 'active': True}}
    '''
    result = {}
    for item in menu_dict.values():
        active = item.get('active')
        menu_id = item['menu_id']
        if menu_id in result:
            result[menu_id]['children'].append({'feature': item['feature'], 'url': item['url'], 'active': active})
            if active:
                result[menu_id]['active'] = True
        else:
            result[menu_id] = {
                'menu_id': item['menu_id'],
                'menu_title': item['menu_title'],
                'active': active,
                'children': [
                    {'feature': item['feature'], 'url': item['url'], 'active': active}
                ]
            }

        '''
        {
            1: {
                'menu_id': 1, 'menu_title': '管理菜单', 'active': None, 
                'children': [
                    {'feature': 'listBooks', 'url': '/listBooks/', 'active': None}, 
                    {'feature': 'listOrders', 'url': '/listOrders/', 'active': None}]}, 
            2: {
                'menu_id': 2, 'menu_title': '导航菜单', 'active': True, 
                'children': [{'feature': 'home', 'url': '/home/', 'active': True}]}}
        '''

    return {"menu_dict": result}


'''

{
    1: {
        'menu_id': 1, 
        'menu_title': '管理菜单', 
        'active': None, 
        'children': [{'feature': 'listBooks', 'url': '/listBooks/', 'active': None}, 
        {'feature': 'listOrders', 'url': '/listOrders/', 'active': None}]}, 
    2: {
        'menu_id': 2, 
        'menu_title': '导航菜单', 
        'active': True, 
        'children': [{'feature': 'home', 'url': '/home/', 'active': True}]}}

'''