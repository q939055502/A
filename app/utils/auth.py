import functools
from flask import request, g
from app.utils.response import api_response
from app.models.user.user import User
from app.services.permission_service import PermissionService
from app.utils.status_codes import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from flask_jwt_extended import get_jwt_identity
from app.utils.logger import logger


def permission_required(resource, action, scope='all', resource_id_param='id'):
    """检查用户是否有指定资源的操作权限

    Args:
        resource (str): 资源名称
        action (str): 操作类型
        scope (str, optional): 权限范围. Defaults to 'all'.
        resource_id_param (str, optional): 资源ID在URL参数中的名称. Defaults to 'id'.
    """
    
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            # 使用JWT获取当前用户ID
            try:
                user_id = get_jwt_identity()
                if not user_id:
                    return api_response(
                    success=False,
                    code=HTTP_401_UNAUTHORIZED,
                    message='未认证，请先登录'
                )
                # 将用户ID设置到g对象中
                g.user_id = user_id
            except Exception as e:
                return api_response(
                    success=False,
                    code=HTTP_401_UNAUTHORIZED,
                    message='未认证，请先登录'
                )

            user = User.query.get(user_id)
            if not user:
                return api_response(
                    success=False,
                    code=HTTP_404_NOT_FOUND,
                    message='用户不存在'
                )

            # 获取资源ID
            resource_id = kwargs.get(resource_id_param) if scope == 'own' else None

            # 检查权限
            has_perm = PermissionService.has_user_permission(user, resource, action, scope, resource_id)
            if not has_perm:
                logger.warning(f'用户 {user_id} 权限不足，需要{resource}:{action}:{scope}权限，请求ID: {getattr(g, "request_id", None)}')
                return api_response(
                    success=False,
                    code=HTTP_403_FORBIDDEN,
                    message=f'权限不足，需要{resource}:{action}:{scope}权限'
                )
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


def role_required(role_name):
    """检查用户是否有指定角色

    Args:
        role_name (str): 角色名称
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            # 使用JWT获取当前用户ID
            try:
                user_id = get_jwt_identity()
                if not user_id:
                    return api_response(
                    success=False,
                    code=HTTP_401_UNAUTHORIZED,
                    message='未认证，请先登录'
                )
            except Exception as e:
                return api_response(
                    success=False,
                    code=HTTP_401_UNAUTHORIZED,
                    message='未认证，请先登录'
                )

            user = User.query.get(user_id)
            if not user:
                return api_response(
                    success=False,
                    code=HTTP_404_NOT_FOUND,
                    message='用户不存在'
                )

            # 检查角色
            has_role = PermissionService.has_user_role(user, role_name)
            if not has_role:
                logger.warning(f'用户 {user_id} 角色不足，需要{role_name}角色权限，请求ID: {getattr(g, "request_id", None)}')
                return api_response(
                    success=False,
                    code=HTTP_403_FORBIDDEN,
                    message=f'需要{role_name}角色权限'
                )
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    """获取当前登录用户

    Returns:
        User: 当前登录用户对象或None
    """
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return None
    return User.query.get(user_id)