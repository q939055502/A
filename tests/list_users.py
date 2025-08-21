from app import create_app
from app.db import db
from app.models import User
from config.development import DevelopmentConfig

# 创建应用实例
app = create_app()

# 手动设置配置
app.config.from_object(DevelopmentConfig)

# 使用应用上下文
with app.app_context():
    # 查询所有用户
    users = User.query.all()
    
    # 打印用户信息
    print(f"数据库中共有 {len(users)} 个用户")
    for user in users:
        print(f"用户ID: {user.id}, 用户名: {user.username}, 状态: {user.status}")