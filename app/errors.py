# app/errors.py
from flask import jsonify, g
from flask_jwt_extended import JWTManager
import time
from app.utils.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from app.utils import generate_request_id
from flask_jwt_extended.exceptions import (
    TokenExpiredError,
    InvalidTokenError,
    NoAuthorizationError,
    TokenBlacklistedError
)

# 初始化JWT管理器（在app/__init__.py中会关联到app）
jwt = JWTManager()

# ------------------------------
# 1. JWT专用异常处理（用@jwt.error_handler）
# ------------------------------
@jwt.error_handler(TokenExpiredError)
def handle_token_expired(e):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"JWT令牌过期: {str(e)}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": HTTP_401_UNAUTHORIZED,
        "message": "令牌已过期，请刷新令牌",
        "requestId": request_id,
        "timestamp": timestamp
    }), HTTP_401_UNAUTHORIZED

@jwt.error_handler(InvalidTokenError)
def handle_invalid_token(e):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"JWT令牌无效: {str(e)}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": HTTP_401_UNAUTHORIZED,
        "message": "令牌无效，请重新登录",
        "requestId": request_id,
        "timestamp": timestamp
    }), HTTP_401_UNAUTHORIZED

@jwt.error_handler(NoAuthorizationError)
def handle_no_authorization(e):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"未检测到JWT令牌: {str(e)}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "未检测到令牌，请先登录",
        "requestId": request_id,
        "timestamp": timestamp
    }), 401

@jwt.error_handler(TokenBlacklistedError)
def handle_token_blacklisted(e):
    request_id = getattr(g, 'request_id', generate_request_id())
    timestamp = int(time.time() * 1000)
    logger.error(f"JWT令牌已被拉黑: {str(e)}, 请求ID: {request_id}")
    return jsonify({
        "success": False,
        "code": 401,
        "message": "令牌已被吊销，请重新登录",
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

    # 可以继续添加其他异常处理，如403（权限不足）等