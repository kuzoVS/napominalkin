from bot.database.models import create_user, get_user, get_user_by_username


def register_user(user_id, username=None, first_name=None):
    create_user(user_id, username, first_name)


def get_user_info(user_id):
    return get_user(user_id)


def find_user_by_username(username: str):
    return get_user_by_username(username)
