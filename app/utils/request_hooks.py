from flask import request, g, current_app
from app.utils.logger import logger


def register_before_request(app):
    """
    注册请求前钩子，用于打印访问令牌和刷新令牌
    
    Args:
        app: Flask 应用实例
    """
    @app.before_request
    def before_request_hook():
        # 打印请求路径
        logger.info(f"请求路径 {request.path}")
        
        # 只在开发环境打印令牌信息
        if current_app.config.get('ENV') == 'development':
            access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            logger.info(f"Authorization----令牌: {access_token}")

# 使用说明:
# 在app/__init__.py中导入并注册此钩子
# from app.utils.request_hooks import register_before_request
# register_before_request(app)