# 开发环境配置
import os
from datetime import timedelta

# 开发环境配置类
# 用途: 存储开发环境下的应用配置
# 使用方法: 无需手动加载，通过config.py中的get_config()函数根据FLASK_ENV自动加载
#          开发环境下(FLASK_ENV=development)会自动使用此类

class DevelopmentConfig:
    # 应用密钥
    # 作用: 用于加密会话数据、表单数据等
    # 使用: 从环境变量获取，未设置时使用默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2e479b50861520b6ebf1b37ea547a5487114784771568f928d0f256aa6eb2c4e'

    # 数据库连接URL
    # 作用: 指定应用连接的数据库
    # 使用: 从环境变量获取，未设置时使用SQLite数据库
    # 直接使用绝对路径，不依赖环境变量
    # MySQL数据库连接配置
    # 请将{username}、{password}、{host}、{port}和{database}替换为实际的MySQL连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/inspection_report?charset=utf8mb4&unix_socket=/tmp/mysql.sock'




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
    # 配置: 开发环境通常允许本地前端地址
    CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # 记住我Cookie有效期
    # 作用: 设置"记住我"功能的Cookie有效期
    # 配置: 根据需求设置，这里设为7天
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # bcrypt哈希轮数
    # 作用: 设置密码哈希的计算强度
    # 配置: 开发环境可设为较低值，生产环境应设为较高值
    BCRYPT_LOG_ROUNDS = 12

    # JWT密钥
    # 作用: 用于JWT令牌的签名和验证
    # 使用: 从环境变量获取，未设置时使用默认值
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'a92b79afb991fb9689b06124fa3382a18b663a0a2170878822226ca91b601bd3'

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
    JWT_TOKEN_LOCATION = ['headers']

    # JWT Cookie安全设置
    # 作用: 是否仅通过HTTPS传输JWT Cookie
    # 配置: 开发环境可设为False，生产环境必须设为True
    JWT_COOKIE_SECURE = False

    # JWT Cookie CSRF保护
    # 作用: 是否启用JWT Cookie的CSRF保护
    # 配置: 建议设为True以提高安全性
    # JWT_COOKIE_CSRF_PROTECT = True

    # 调试模式
    # 作用: 是否启用调试模式
    # 配置: 开发环境可设为True，生产环境必须设为False
    DEBUG = True

    # 邮件服务器配置
    # 开发环境使用默认配置，生产环境从环境变量获取
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_PORT = 587  # 邮件服务器端口（通常为587或465）
    MAIL_USE_TLS = True  # 使用TLS加密
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '939055502@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'ncvljspjtufnbgad'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME  # 默认发件人

    # 验证码配置
    # 禁用短信验证码，只使用邮箱验证码
    ENABLE_SMS_CODE = False
    ENABLE_EMAIL_CODE = True

    # 服务器配置
    IP = '127.0.0.1'
    PORT = 5000

    # 日志配置
    LOG_LEVEL = 'DEBUG'#'INFO'
    LOG_FILE = 'app.log'

    # 功能开关
    ENABLE_DEMO_DATA = False
    ENABLE_AUTO_BACKUP = True

    # 应用域名
    # 作用: 指定应用的域名，用于生成外部链接
    # 配置: 开发环境通常使用localhost或127.0.0.1
    DOMAIN = os.environ.get('DOMAIN') #or 'http://localhost:5000'

    # API配置
    API_TIMEOUT = 30
    API_BASE_URL = 'http://api.example.com'

    # 第三方服务配置
    QR_CODE_SERVICE_URL = 'https://unpkg.com/qrcode.js@1.0.0/qrcode.min.js'