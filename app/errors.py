# app/errors.py
from flask import jsonify, g, request
from flask_jwt_extended import JWTManager
import time
from app.utils.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from app.utils.logger import logger
from app.utils import generate_request_id
# 不再需要直接导入JWT异常类，因为使用了回调函数处理异常


# 初始化JWT管理器（在app/__init__.py中会关联到app）
jwt = JWTManager()

# ------------------------------
# 1. JWT专用异常处理（使用回调函数）
# ------------------------------
@jwt.unauthorized_loader
def handle_unauthorized_callback(error_string):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"未授权访问: {error_string}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "未检测到令牌，请先登录",
        "requestId": request_id,
        "timestamp": timestamp
    }), 401

@jwt.revoked_token_loader
def handle_revoked_token_callback(jwt_header, jwt_data):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"令牌已被撤销: {jwt_data}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "令牌已被撤销，请重新登录",
        "requestId": request_id,
        "timestamp": timestamp
    }), 401

@jwt.invalid_token_loader
def handle_invalid_token_callback(error_string):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"无效令牌: {error_string}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "令牌无效，请重新登录",
        "requestId": request_id,
        "timestamp": timestamp
    }), 401

@jwt.needs_fresh_token_loader
def handle_needs_fresh_token_callback(jwt_header, jwt_data):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"需要新鲜令牌: {jwt_data}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "需要重新登录以获取新鲜令牌",
        "requestId": request_id,
        "timestamp": timestamp
    }), 401

# ------------------------------
# 2. 全局通用异常处理（用@app.error_handler）
# ------------------------------
def register_global_errors(app):
    # 处理400错误（请求参数错误）
    @app.errorhandler(HTTP_400_BAD_REQUEST)
    def bad_request(e):
        request_id = getattr(g, 'request_id', generate_request_id())
        timestamp = int(time.time() * 1000)
        logger.error(f"请求参数错误: {str(e)}, 请求ID: {request_id}")
        return jsonify({
            "success": False,
            "code": HTTP_400_BAD_REQUEST,
            "message": "请求参数错误，请检查输入",
            "requestId": request_id,
            "timestamp": timestamp
        }), HTTP_400_BAD_REQUEST

    # 处理404错误（接口不存在）
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def not_found(e):
        request_id = getattr(g, 'request_id', generate_request_id())
        timestamp = int(time.time() * 1000)
        # 获取请求URL和端口信息
        request_url = request.url
        host = request.host
        logger.error(f"请求的接口不存在: {str(e)}, 请求URL: {request_url}, 请求主机: {host}, 请求ID: {request_id}")
        return jsonify({
            "success": False,
            "code": HTTP_404_NOT_FOUND,
            "message": "请求的接口不存在",
            "requestId": request_id,
            "timestamp": timestamp
        }), HTTP_404_NOT_FOUND

    # 处理500错误（服务器内部错误）
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def server_error(e):
        app.logger.error(f"服务器错误: {str(e)}")  # 记录错误日志
        request_id = getattr(g, 'request_id', generate_request_id())
        timestamp = int(time.time() * 1000)
        return jsonify({
            "success": False,
            "code": HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "服务器内部错误，请稍后重试",
            "requestId": request_id,
            "timestamp": timestamp
        }), HTTP_500_INTERNAL_SERVER_ERROR

        # 处理403错误（权限不足）
    @app.errorhandler(HTTP_403_FORBIDDEN)
    def forbidden(e):
        request_id = getattr(g, 'request_id', generate_request_id())
        timestamp = int(time.time() * 1000)
        app.logger.error(f"权限不足: {str(e)}, 请求ID: {request_id}")
        return jsonify({
            "success": False,
            "code": HTTP_403_FORBIDDEN,
            "message": "权限不足，无法执行此操作",
            "requestId": request_id,
            "timestamp": timestamp
        }), HTTP_403_FORBIDDEN

    # 可以继续添加其他异常处理