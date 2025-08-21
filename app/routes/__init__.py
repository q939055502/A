"""路由初始化模块

此模块负责导入和注册所有路由蓝图
"""

from flask import Flask

# 导入路由模块


# 导入新拆分的用户、权限、报告和人员管理路由模块
from app.routes.report.report_routes import report_bp
from app.routes.user.user_routes import user_bp
from app.routes.user.auth_routes import auth_bp
from app.routes.admin.admin import admin_bp
from app.routes.announcement.announcement_routes import announcement_bp


def register_routes(app: Flask):
    """注册所有路由蓝图到Flask应用

    Args:
        app (Flask): Flask应用实例
    """
    # 注册路由蓝图

    app.register_blueprint(report_bp)
    
    # 注册新拆分的用户和权限路由蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # 注册公告路由蓝图
    app.register_blueprint(announcement_bp)
    
    return app