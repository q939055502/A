"""响应工具模块
提供统一的API响应格式生成功能
"""
from flask import jsonify, g, request
from .app_uuid import generate_request_id
from .date_time import get_timestamp
from .status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR
)

def api_response(success=True, code=HTTP_200_OK, message="", data=None, request_id=None, access_token=None, refresh_token=None):
    """生成统一格式的API响应

    生成包含标准格式的API响应，包括状态、代码、消息、请求ID和时间戳。
    同时将requestId添加到响应头中。

    Args:
        success (bool, optional): 操作是否成功. Defaults to True.
        code (int, optional): HTTP状态码. Defaults to 200.
        message (str, optional): 响应消息. Defaults to "".
        data (any, optional): 响应数据. Defaults to None.
        request_id (str, optional): 请求ID. Defaults to None.

    Returns:
        tuple: (Flask响应对象, HTTP状态码)
    """



    # 统一请求ID获取逻辑：优先从g中获取，其次是传入的参数，最后生成新的
    request_id = getattr(g, 'request_id', request_id) or generate_request_id()
    response_data = {
        "success": success,
        "code": code,
        "message": message,
        "requestId": request_id,
        "timestamp": get_timestamp(),
        "data": data,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    
    return jsonify(response_data), code

def validate_request_data(required_fields=None):
    """验证请求数据格式和必填字段

    验证请求是否包含JSON数据，并检查必填字段是否存在。

    Args:
        required_fields (list, optional): 必填字段列表. Defaults to None.

    Returns:
        tuple: (数据字典, 错误响应元组) 如果验证通过，错误响应为None
    """
    try:
        data = request.get_json()
        if not data:
            return None, api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message="请求数据格式错误，请提供JSON数据"
            )

        if required_fields:
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            if missing_fields:
                return None, api_response(
                    success=False,
                    code=HTTP_400_BAD_REQUEST,
                    message=f"请提供以下必填字段: {', '.join(missing_fields)}"
                )

        return data, None
    except Exception as e:
        return None, api_response(
            success=False,
            code=HTTP_400_BAD_REQUEST,
            message=f"请求数据解析错误: {str(e)}"
        )

from .logger import logger

def handle_exception(e, default_message="操作失败"):
    """统一异常处理

    处理API调用中的异常，返回标准化的错误响应，并记录异常日志。

    Args:
        e (Exception): 捕获的异常
        default_message (str, optional): 默认错误消息. Defaults to "操作失败".

    Returns:
        tuple: Flask响应对象和HTTP状态码
    """
    request_id = getattr(g, 'request_id', generate_request_id())
    logger.error(f"{default_message}: {str(e)}, 请求ID: {request_id}")
    return api_response(
        success=False,
        code=HTTP_500_INTERNAL_SERVER_ERROR,
        message=f"{default_message}: {str(e)}"
    )



    