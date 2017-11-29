class BasePagePermission:
    """
        初始化并提供渲染模板权限的基本验证函数
    """

    def __init__(self, feature_list):
        self.feature_list = feature_list

    def has_home(self):
        if 'home' in self.feature_list:
            return True


class BaseBookPermission(BasePagePermission):
    """
        用于模板中渲染图书组权限
    """

    def has_showbooks(self):
        if 'showbooks' in self.feature_list:
            return True

    def has_addbook(self):
        if 'addbook' in self.feature_list:
            return True

    def has_delbook(self):
        if 'delbook' in self.feature_list:
            return True

    def has_editbook(self):
        if 'editbook' in self.feature_list:
            return True
