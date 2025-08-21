"""工具包

此包包含各种工具函数，用于简化应用程序开发。
提供的功能包括UUID生成、时间处理和API响应格式化等。

使用示例:
    from app.utils import generate_request_id, get_timestamp, api_response

    # 生成请求ID
    request_id = generate_request_id()

    # 生成时间戳
    timestamp = get_timestamp()

    # 生成API响应
    return api_response(success=True, data={'key': 'value'})
"""
from .app_uuid import generate_request_id
from .date_time import get_timestamp
from .response import api_response

__all__ = [
    'generate_request_id',
    'get_timestamp',
    'api_response'
]