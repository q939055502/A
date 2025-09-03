from app import create_app
from app.models.user.user import User
from app.db import db

# 创建应用实例
app = create_app()

# 在应用上下文中执行查询
with app.app_context():
    # 查询用户数量
    total_users = db.session.query(User).count()
    active_users = db.session.query(User).filter_by(status=1, deleted_at=None).count()
    
    print(f"用户总数: {total_users}")
    print(f"活跃用户数: {active_users}")