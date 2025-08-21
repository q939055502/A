"""权限、Token路由模块

功能: 处理用户登出、令牌刷新和权限验证的API请求
auth_routes.py  # 权限、token路由
主要接口:
- POST /auth/logout: 用户登出，清除认证状态
- POST /auth/refresh: 刷新访问令牌
- GET /auth/verify: 验证登录状态
- GET /auth/get-user-info: 获取用户信息
"""

from flask import Blueprint, request, jsonify, g
from app.utils.status_codes import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from app.db import db
from app.models.user.user import User
from app.models.token import TokenBlocklist
from flask_jwt_extended import (
    jwt_required,  # JWT认证装饰器
    get_jwt,
    get_jwt_identity
)
from flask_jwt_extended.utils import unset_jwt_cookies
from app.utils.jwt import handle_refresh, check_if_token_in_blocklist
from app.utils.response import api_response, handle_exception
from app.utils.logger import logger
from app.services.user.user_service import UserService

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


   
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌和刷新令牌
    
    Returns:
        Response: 包含新访问令牌和新刷新令牌的响应
    """
    try:
        # 调用jwt工具中的handle_refresh函数处理令牌刷新逻辑
        success, new_access_token, new_refresh_token, message = handle_refresh()
        
        if success:
            return api_response(
                success=success,
                code=HTTP_200_OK,
                message=message,
                refresh_token=new_refresh_token,
                access_token=new_access_token,
                data={
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                },
            )
        else:
            return api_response(
                success=success,
                code=HTTP_401_UNAUTHORIZED,
                message=message,
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                data={
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token
                },
            )
    except Exception as e:
        return handle_exception(e, "刷新令牌失败")

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_login():
    """验证用户登录状态

    验证当前用户是否已登录，返回用户信息和权限

    Returns:
        tuple: 包含统一格式响应的元组
    """
    from app.services.user.user_service import UserService

    # 直接返回verify_login_status方法的结果(响应对象, 状态码)
    return UserService.verify_login_status()