from app.models.user.user import User


def get_user_nickname(user_id):
    """根据用户ID获取用户昵称，如果没有则返回用户名

    Args:
        user_id: 用户ID，可以是字符串或数字

    Returns:
        str: 用户昵称或用户名，如果用户不存在或ID无效则返回空字符串
    """
    # 尝试将用户ID转换为int
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return ""
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return ""
    # 返回昵称或用户名
    return user.nickname if user.nickname else user.username