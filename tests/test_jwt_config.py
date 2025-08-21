import os
import sys
from datetime import timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# 加载环境变量
os.environ['FLASK_ENV'] = 'development'

# 创建应用实例
app = create_app()

# 在应用上下文中打印配置
with app.app_context():
    # 打印JWT相关配置
    print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
    print(f"JWT_REFRESH_TOKEN_EXPIRES: {app.config.get('JWT_REFRESH_TOKEN_EXPIRES')}")
    print(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')}")
    print(f"JWT_TOKEN_LOCATION: {app.config.get('JWT_TOKEN_LOCATION')}")

    # 验证配置是否正确加载
    if app.config.get('JWT_ACCESS_TOKEN_EXPIRES') == timedelta(minutes=30):
        print("JWT_ACCESS_TOKEN_EXPIRES 配置正确加载")
    else:
        print("JWT_ACCESS_TOKEN_EXPIRES 配置加载错误")