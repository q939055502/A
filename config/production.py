# 生产环境配置
import os
from datetime import timedelta

# 生产环境配置类
# 用途: 存储生产环境下的应用配置
# 使用方法: 无需手动加载，通过config.py中的get_config()函数根据FLASK_ENV自动加载
#          生产环境下(FLASK_ENV=production)会自动使用此类

class ProductionConfig:
    # 应用密钥
    # 作用: 用于加密会话数据、表单数据等
    # 使用: 必须从环境变量获取
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # 数据库连接URL
    # 作用: 指定应用连接的数据库
    # 使用: 必须从环境变量获取
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # 跟踪修改
    # 作用: 是否跟踪对象修改
    # 配置: 建议设为False以提高性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS凭证支持
    # 作用: 是否允许跨域请求携带凭证
    # 配置: 当前端需要携带Cookie等凭证时设为True
    CORS_SUPPORTS_CREDENTIALS = True

    # 允许的CORS源
    # 作用: 指定允许跨域请求的来源
    # 使用: 从环境变量获取，逗号分隔多个值
    # 配置: 生产环境应限制为可信的前端地址
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

    # 记住我Cookie有效期
    # 作用: 设置"记住我"功能的Cookie有效期
    # 配置: 根据需求设置，这里设为7天
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # bcrypt哈希轮数
    # 作用: 设置密码哈希的计算强度
    # 配置: 生产环境应设为较高值以提高安全性
    BCRYPT_LOG_ROUNDS = 12

    # JWT密钥
    # 作用: 用于JWT令牌的签名和验证
    # 使用: 必须从环境变量获取
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # 访问令牌过期时间
    # 作用: 设置JWT访问令牌的过期时间
    # 配置: 根据安全性要求设置，这里设为30分钟
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

    # 刷新令牌过期时间
    # 作用: 设置JWT刷新令牌的过期时间
    # 配置: 根据需求设置，这里设为3天
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=3)

    # 令牌位置
    # 作用: 指定从哪里获取JWT令牌
    # 配置: 可以从请求头或Cookie中获取
    JWT_TOKEN_LOCATION = ['headers', 'cookies']

    # JWT Cookie安全设置
    # 作用: 是否仅通过HTTPS传输JWT Cookie
    # 配置: 生产环境必须设为True
    JWT_COOKIE_SECURE = True

    # JWT Cookie CSRF保护
    # 作用: 是否启用JWT Cookie的CSRF保护
    # 配置: 建议设为True以提高安全性
    JWT_COOKIE_CSRF_PROTECT = True

    # 调试模式
    # 作用: 是否启用调试模式
    # 配置: 生产环境必须设为False
    DEBUG = False

    # 邮件服务器配置
    # 作用: 配置应用发送邮件的服务器信息
    # 配置: 必须从环境变量获取，确保生产环境中设置了必要的环境变量
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # 服务器配置
    IP = '0.0.0.0'
    PORT = 5000

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'

    # 功能开关

    # 应用域名
    # 作用: 指定应用的域名，用于生成外部链接
    # 配置: 生产环境必须从环境变量获取
    DOMAIN = os.environ.get('DOMAIN')
    
    # 配置: 生产环境必须从环境变量获取
    ENABLE_DEMO_DATA = False
    ENABLE_AUTO_BACKUP = True

    # API配置
    API_TIMEOUT = 30
    API_BASE_URL = 'http://api.example.com'

    # 第三方服务配置
    QR_CODE_SERVICE_URL = 'https://unpkg.com/qrcode.js@1.0.0/qrcode.min.js'

# 确保生产环境中设置了必要的环境变量
# 说明: 生产环境必须设置这些环境变量，否则会抛出异常
if not ProductionConfig.SECRET_KEY:
    raise ValueError("No SECRET_KEY set for production environment")
if not ProductionConfig.SQLALCHEMY_DATABASE_URI:
    raise ValueError("No DATABASE_URL set for production environment")
if not ProductionConfig.JWT_SECRET_KEY:
    raise ValueError("No JWT_SECRET_KEY set for production environment")
if not ProductionConfig.MAIL_SERVER or not ProductionConfig.MAIL_USERNAME or not ProductionConfig.MAIL_PASSWORD:
    raise ValueError("Mail server configuration is missing for production environment")

