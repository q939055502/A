from app import create_app
from app.db import db

# 创建Flask应用
app = create_app()

# 在应用上下文中创建数据库表
with app.app_context():
    try:
        # 创建所有表
        db.create_all()
        print("成功创建数据库表")
    except Exception as e:
        print(f"创建数据库表时出错: {str(e)}")