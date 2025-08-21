"""用户登录、注册路由模块

功能: 处理用户登录和注册的API请求
user_routes.py  # 用户登录、注册路由
主要接口:
- POST /auth/login: 用户登录，返回访问令牌
- POST /auth/register: 用户注册
- POST /auth/send-email-verification: 发送邮箱验证码
"""

from flask import Blueprint, request, jsonify, g
from app.utils.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from werkzeug.security import check_password_hash
from app.db import db
from app.models.user.user import User
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.permission_service import PermissionService
from app.utils.auth import permission_required
from app.utils.jwt import generate_tokens, unset_jwt_cookies
from app.utils.response import api_response, validate_request_data, handle_exception
from app.utils.logger import logger
import random
import time
import redis
import os
from app.services.user.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt

# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
REDIS_DB = int(os.environ.get('REDIS_DB') or 0)

# 创建Redis客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# 邮箱验证码过期时间（秒）
EMAIL_CODE_EXPIRE = 300

# 邮箱发送间隔（秒）
EMAIL_SEND_INTERVAL = 60

# 内存存储，用于Redis不可用的情况
email_memory_storage = {}

# 检查Redis连接状态的函数
def is_redis_available():
    try:
        return redis_client.ping()
    except:
        return False

# 从UserService导入所需的方法
from app.services.user.user_service import UserService
# 从schemas导入UserLogin模型
from app.utils.schemas import UserLogin
from pydantic import ValidationError

# 导入必要的模块
from flask import request
from http import HTTPStatus

# 创建蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/login', methods=['POST'])
def api_login():
    try:
        # 使用Pydantic模型验证请求数据
        data = request.get_json()
        if not data:
            return api_response(
                success=False,
                code=HTTPStatus.BAD_REQUEST,
                message="请求数据格式错误，请提供JSON数据"
            )
        # 使用UserLogin模型验证数据
        try:
            login_data = UserLogin(**data)
            
        except ValidationError as e:
            # 提取验证错误信息
            errors = e.errors()
            error_messages = []
            for error in errors:
                field = error.get('loc', ['unknown'])[0]
                msg = error.get('msg', '验证失败')
                error_messages.append(f"{field}: {msg}")
            
            return api_response(
                success=False,
                code=HTTPStatus.BAD_REQUEST,
                message=", ".join(error_messages)
            )

        username = login_data.username
        password = login_data.password
        remember_me = login_data.remember_me
        request_id = login_data.request_id
        # 使用UserService.login方法进行登录
        user, access_token, refresh_token, request_id, error = UserService.login(username, password, remember_me, request_id)
        if error:
            return api_response(
                success=False,
                code=HTTP_401_UNAUTHORIZED,
                message=error,
                request_id=request_id
            )
        
        # 使用user对象的to_dict方法获取用户数据
        user_data = user.to_dict()
        # 获取用户的角色和权限信息（包括直接拥有和通过角色获得的权限）
        
        roles_and_permissions = PermissionService.get_roles_and_permissions(user)
        
        user_data['roles'] = roles_and_permissions['roles']
        user_data['permissions'] = roles_and_permissions['permissions']
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
        }
        print(access_token)
        print(refresh_token)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message="登录成功",
            data=data,
            access_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        return handle_exception(e, "登录失败")

@user_bp.route('/register', methods=['POST'])
def api_register():
    try:
        # 验证请求数据
        required_fields = ['username', 'email', 'password', 'email_code']
        data, error_response = validate_request_data(required_fields)
        if error_response:
            logger.warning(f'注册请求数据验证失败: {error_response[0].json}')
            return error_response

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        nickname = data.get('nickname')

        logger.info(f'用户注册请求: 用户名={username}, 邮箱={email}')

        # 验证邮箱验证码（注册类型）
        email_code = data.get('email_code')
        success, message = UserService.verify_email_code(email, email_code, code_type='register')
        if not success:
            logger.warning(f'邮箱验证码验证失败: {message}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )

        # 准备注册数据
        register_data = {
            'username': username,
            'email': email,
            'password': password,
            'nickname': nickname
        }

        # 调用UserService注册用户
        new_user, error = UserService.register_user(register_data)
        if error:
            logger.warning(f'用户注册失败: {error}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=error
            )
        print('7777777777777777777777777777777777777777777')
        # 为新用户分配角色和权限
        success, error = UserService.assign_user_role_and_permissions(new_user)
        if not success:
            logger.warning(f'为用户分配角色和权限失败: {error}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=error
            )
        print('66666666666666666666666666666666666666666666')
        # 生成令牌，默认不记住密码
        access_token, refresh_token = generate_tokens(new_user.id, remember_me=False)
        # 获取用户数据
        user_data = new_user.to_dict()
        print(user_data)
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
        }
        print('33333333333333333333333333333333333333333')
        return api_response(
            success=True,
            code=HTTP_201_CREATED,
            message="注册成功",
            data=data,
            access_token=access_token,
            refresh_token=refresh_token
        )
    except Exception as e:
        return handle_exception(e, "注册失败")


@user_bp.route('/send-register-code', methods=['POST'])#发送注册验证码
def send_register_code():
    try:
        # 验证请求数据
        data, error_response = validate_request_data(['email'])
        if error_response:
            logger.warning(f'发送邮箱验证码请求数据验证失败: {error_response[0].json}')
            return error_response

        email = data.get('email')
        logger.info(f'尝试发送邮箱验证码到: {email}')

        # 检查邮箱是否已被注册
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            logger.warning(f'邮箱 {email} 已被注册')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message="该邮箱已被注册"
            )

        # 发送注册验证码 - 注册流程不检查用户存在
        success, message = UserService.send_email_code(email, code_type='register', check_user_exists=False)
        if not success:
            logger.warning(f'发送邮箱验证码失败: {message}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message="邮箱验证码发送成功，请在5分钟内完成验证"
        )
    except Exception as e:
        return handle_exception(e, "发送邮箱验证码失败")

@user_bp.route('/send-reset-code', methods=['POST'])#发送重置验证码
def send_reset_code():
    """发送密码重置验证码

    请求体参数:
    - email: 用户邮箱

    返回:
    - 成功: 200, 消息
    - 失败: 400/404, 错误消息
    """
    try:
        # 验证请求数据
        data, error_response = validate_request_data(['email'])
        if error_response:
            logger.warning(f'发送重置验证码请求数据验证失败: {error_response[0].json}')
            return error_response

        email = data.get('email')
        logger.info(f'尝试发送密码重置验证码到: {email}')

        # 发送密码重置验证码
        success, message = UserService.send_email_code(email, code_type='reset_password', check_user_exists=True)
        if not success:
            logger.warning(f'发送密码重置验证码失败: {message}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message="密码重置验证码已发送到您的邮箱，请查收"
        )
    except Exception as e:
        return handle_exception(e, "发送密码重置验证码失败")


@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        # 验证请求数据
        data, error_response = validate_request_data(['email'])
        if error_response:
            logger.warning(f'忘记密码请求数据验证失败: {error_response[0].json}')
            return error_response

        email = data.get('email')
        logger.info(f'用户忘记密码请求: 邮箱={email}')

        # 调用UserService处理忘记密码逻辑
        success, message = UserService.generate_password_reset_token_and_send_email(email)
        if success:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message=message
            )
        else:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )
    except Exception as e:
        return handle_exception(e, "处理忘记密码请求失败")

@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        # 验证请求数据
        data, error_response = validate_request_data(['token', 'new_password'])
        if error_response:
            logger.warning(f'重置密码请求数据验证失败: {error_response[0].json}')
            return error_response

        token = data.get('token')
        new_password = data.get('new_password')
        logger.info(f'用户密码重置请求: 令牌={token[:5]}...')  # 仅记录令牌前5位，保护安全

        # 调用UserService处理密码重置逻辑
        success, message = UserService.reset_user_password(token, new_password)
        if success:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message=message
            )
        else:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )
    except Exception as e:
        return handle_exception(e, "处理密码重置请求失败")

@user_bp.route('/reset-password-by-code', methods=['POST'])
def reset_password_by_code():
    """通过邮箱验证码重置密码

    请求体参数:
    - email: 用户邮箱
    - code: 验证码
    - new_password: 新密码

    返回:
    - 成功: 200, 消息
    - 失败: 400, 错误消息
    """
    try:
        # 验证请求数据
        required_fields = ['email', 'code', 'new_password']
        data, error_response = validate_request_data(required_fields)
        if error_response:
            logger.warning(f'通过验证码重置密码请求数据验证失败: {error_response[0].json}')
            return error_response

        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')
        logger.info(f'用户通过验证码重置密码请求: 邮箱={email}')

        # 调用UserService处理通过验证码重置密码逻辑
        # 先验证验证码
        verify_success, verify_message = UserService.verify_email_code(email, code, code_type='reset_password')
        if not verify_success:
            logger.warning(f'邮箱验证码验证失败: {verify_message}')
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=verify_message
            )
        
        # 验证通过后重置密码
        success, message = UserService.reset_password_by_email_code(email, new_password)
        if success:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message=message
            )
        else:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )
    except Exception as e:
        return handle_exception(e, "通过验证码重置密码失败")

@user_bp.route('/profile', methods=['POST'])
@permission_required('user', 'update','own')
def update_user_profile():
    """更新用户资料

    请求体参数:
    - nickname: 用户昵称
    - phone_number: 手机号
    - avatar: 头像URL
    - gender: 性别(0-未知、1-男、2-女)
    - birthday: 出生日期(YYYY-MM-DD)
    - address: 地址
    - bio: 个人简介
    - ext_info: 扩展信息(JSON格式)

    返回:
    - 成功: 200, 消息
    - 失败: 400/401, 错误消息
    """
    try:
        # 获取当前用户ID
        current_user_id = get_jwt_identity()

        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message="请求数据不能为空"
            )

        logger.info(f'用户 {current_user_id} 请求更新资料')

        # 调用UserService处理更新资料逻辑
        success, message = UserService.update_user_profile(current_user_id, data)
        if success:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message=message
            )
        else:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message=message
            )
    except Exception as e:
        return handle_exception(e, "更新用户资料失败")


@user_bp.route('/get-user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前登录用户的详细信息
    
    Returns:
        Response: 包含用户信息的响应
    """
    print('获得用户信息++++++++++++++++++++++++++')
    try:
        # 获取当前用户标识
        current_user_id = get_jwt_identity()
        # 调用UserService获取用户信息
        success, result = UserService.get_user_info(current_user_id)
        if not success:
            return api_response(
                success=False,
                code=404,
                message=result
            )
        
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message="获取用户信息成功",
            data=result
        )
    except Exception as e:
        return handle_exception(e, "获取用户信息失败")





@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """处理用户登出逻辑
    
    Returns:
        Response: 包含登出结果的响应
    """
    try:
        # 获取当前用户标识
        current_user_id = get_jwt_identity()
        # 查询用户
        user = User.query.get(current_user_id)
        if not user:
            response = api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message="用户不存在"
            )[0]
            unset_jwt_cookies(response)
            return response
        
        # 获取请求中的refresh_token
        data = request.get_json() or {}
        refresh_token = data.get('refresh_token')
        
        # 获取访问令牌
        access_token = request.headers.get('Authorization', '').replace('Bearer ', '')

        # 调用用户服务的logout方法
        success, message = UserService.logout(user_id=current_user_id, access_token=access_token, refresh_token=refresh_token)
        if not success:
            response = api_response(
                success=False,
                code=HTTP_500_INTERNAL_SERVER_ERROR,
                message=message
            )[0]
            unset_jwt_cookies(response)
            return response
        
        # 创建响应
        response = api_response(
            success=True,
            code=HTTP_200_OK,
            message="登出成功"
        )[0]
        
        # 清除JWT cookie
        unset_jwt_cookies(response)
        
        return response
    except Exception as e:
        return handle_exception(e, "登出失败")