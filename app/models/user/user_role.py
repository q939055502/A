from app.db import db
from datetime import datetime, timezone

# 用户-角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc)),
    db.Column('created_by', db.Integer, db.ForeignKey('users.id')),
    db.Column('is_active', db.Boolean, default=True)
)

# 导入关联表到models包中，方便其他模块使用
__all__ = ['user_roles']