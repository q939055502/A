# 终端运行flask routes 查看URL
import os
from flask import Flask, request, jsonify, g
from app.utils.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import get_config


# 初始化扩展（在模块级别）
jwt = JWTManager()
mail = Mail()

from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    RevokedTokenError,
    JWTDecodeError,
    WrongTokenError,
    FreshTokenRequired
)

# 导入项目模块
from app.db import db

# 延迟导入路由模块，避免循环依赖
# 在create_app函数内部导入路由模块

def create_app():
    # 延迟导入配置，避免循环依赖
    from config import Config
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__
        # 注意：静态文件和模板文件目录配置已注释，因为'a-v'目录不存在
        # static_folder=os.path.join(basedir, '../a-v/dist'),
        # template_folder=os.path.join(basedir, '../a-v/dist')
    )
    
    # 从配置对象加载配置（会自动根据环境选择development或production配置）
    app.config.from_object(Config)
    # 初始化邮件服务
    mail.init_app(app)
    # 初始化CORS
    CORS(app, supports_credentials=True, origins='*',

     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    #, origins="*", methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"]
    # 导入工具函数
    from app.utils import generate_request_id

    # 添加请求拦截器，生成requestId
    @app.before_request
    def before_request():
        # 生成requestId并存储在g对象中
        g.request_id = generate_request_id()
        # 可以从请求头中获取（如果前端传递）
        # g.request_id = request.headers.get('X-Request-Id', generate_request_id())

    # 添加响应拦截器，将requestId添加到响应头
    @app.after_request
    def after_request(response):
        # 将requestId添加到响应头
        response.headers['X-Request-Id'] = g.request_id
        return response

    # 初始化数据库和迁移工具
    db.init_app(app)
    migrate = Migrate(app, db)  # 绑定应用和数据库到Migrate
    
    # 在应用上下文中导入模型，确保迁移工具能识别
    with app.app_context():
        from app.models.report.inspection_report import InspectionReport
        from app.models import TokenBlocklist
        from app.models.user import User
        # 确保所有模型都被导入，以便迁移工具检测

    # 导入JWT处理函数和工具
    from app.utils.jwt import process_logout_token, jwt as jwt_instance
    jwt = jwt_instance
    # 初始化JWT
    jwt.init_app(app)
    
    # 导入并注册请求前钩子
    from app.utils.request_hooks import register_before_request
    register_before_request(app)
    
    # 配置日志系统
    from app.utils.logger import setup_logger
    setup_logger(app)
    
    # ------------------------------
    # JWT相关配置和处理
    # ------------------------------
    
    
    
    # JWT异常处理
    @jwt.unauthorized_loader
    def handle_no_authorization(e):
        return jsonify({
            "success": False,
            "message": "未检测到令牌，请先登录"
        }), HTTP_401_UNAUTHORIZED

    @jwt.revoked_token_loader
    def handle_token_revoked(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "令牌已被吊销或已过期，请重新登录"
        }), HTTP_401_UNAUTHORIZED

    @jwt.invalid_token_loader
    def handle_jwt_decode_error(e):
        return jsonify({
            "success": False,
            "message": "令牌无效，请重新登录"
        }), 401
    
    # ------------------------------
    # 全局异常处理
    # ------------------------------
    
    # 导入并注册全局异常处理
    from app.errors import register_global_errors
    register_global_errors(app)
    
    # ------------------------------
    # 注册蓝图和CLI命令
    # ------------------------------
    
    # 导入路由注册函数
    from app.routes import register_routes

    # 注册所有路由蓝图
    register_routes(app)


    # 初始化命令
    from app.commands import init_commands
    init_commands(app)



    # 注册CLI命令查看路由
    @app.cli.command("routes")
    def list_routes():
        print("\n注册的路由:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} ({', '.join(rule.methods)})")
        print()
    
    return app
