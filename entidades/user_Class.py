class User_Class:
    def __init__(self, class_user=None):
        if class_user:
            self.class_user = class_user
        else:
            self.class_user = "Peasant"