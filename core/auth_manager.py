_current_user  = None

def set_user(user):
    global _current_user
    _current_user = user

def get_user():
    return _current_user

def logout():
    global _current_user
    _current_user = None