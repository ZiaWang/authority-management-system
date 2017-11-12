class BasePagePermission:
    def __init__(self, feature_list):
        self.feature_list = feature_list

    def has_home(self):
        if 'home' in self.feature_list:
            return True


class BaseBookPermission(BasePagePermission):
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
