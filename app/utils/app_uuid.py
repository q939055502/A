"""UUID工具模块
提供生成唯一标识符的工具函数
"""
import uuid

def generate_request_id():
    """生成唯一请求ID

    使用UUID4算法生成随机的唯一标识符，
    用于标识API请求，方便日志跟踪和问题排查。

    Returns:
        str: 唯一请求ID字符串
    """
    return str(uuid.uuid4())

def generate_order_id(user_id=None):
    """
    生成订单号
    格式: 时间戳(10位)+用户ID(可选)+随机数(4位)
    Args:
        user_id (str, optional): 用户ID
    Returns:
        str: 订单号字符串
    """
    timestamp = str(int(time.time()))
    random_part = str(uuid.uuid4().hex[:4]).upper()
    if user_id:
        return f"{timestamp}{user_id}{random_part}"
    return f"{timestamp}{random_part}"
    