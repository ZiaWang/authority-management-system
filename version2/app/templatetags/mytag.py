from django.template import Library
from django.conf import settings
from re import match

register = Library()


@register.inclusion_tag(filename='menu.html')
def menu_html(request):
    """生成一个菜单页面
    Args:
        request: 请求对象
    Return:
        context_dict: 一个上下文字典，存放用户渲染menu.html的数据
    """

    current_url = request.path_info
    menu_dict = {}
    menu_list = request.session.get(settings.MENU_LIST)
    for item in menu_list:
        menu_id = item['menu_id']
        menu_title = item['menu_title']
        title = item['feature']
        url = item['url']
        active = item['active']

        regex = f'^{url}$'
        if match(pattern=regex, string=current_url):
            active = True

        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append({"title": title, "url": url, "active": active})
            if active:
                menu_dict[menu_id]['active'] = True
        else:
            menu_dict[menu_id] = {
                "menu_id": menu_id,
                "menu_title": menu_title,
                "active": active,
                "children": [
                    {"title": title, "url": url, "active": active}
                ]
            }

    return {'menu_dict': menu_dict}