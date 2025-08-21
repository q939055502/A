import uuid
from app.db import db  # 导入数据库实例
from datetime import datetime, timezone  # 导入日期时间相关模块

class Permission(db.Model):
    """权限模型类
    用于表示系统中的权限，定义了对资源的操作许可
    """
    __tablename__ = 'permissions'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, index=True)  # 权限ID，主键，索引
    code = db.Column(db.String(100), unique=True, index=True, nullable=False)  # 权限代码，唯一，索引，非空
    resource = db.Column(db.String(50), nullable=False)  # 资源名称，非空
    action = db.Column(db.String(50), nullable=False)  # 操作类型，非空
    scope = db.Column(db.String(50), default='all')  # 权限范围，默认为'all'，可选值：'all', 'own', 'specific'
    description = db.Column(db.String(200))  # 权限描述
    is_active = db.Column(db.Boolean, default=True)  # 是否激活，默认为True
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间，自动更新
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人ID，外键关联users表

    def __repr__(self):
        """返回权限的字符串表示"""
        return f'<Permission {self.code} (ID: {self.id})>'

    def __hash__(self):
        """定义Permission对象的哈希方法，使其可以用于集合操作

        Returns:
            int: 基于权限ID的哈希值
        """
        return hash(self.id)

    @staticmethod
    def create_permission(code, resource, action, scope='all', description=None, commit=True):
        """创建新权限

        Args:
            code (str): 权限代码，必须唯一
            resource (str): 资源名称
            action (str): 操作类型
            scope (str, optional): 权限范围. Defaults to 'all'.
            description (str, optional): 权限描述. Defaults to None.
            commit (bool, optional): 是否立即提交到数据库. Defaults to True.

        Returns:
            Permission: 创建的权限对象

        Raises:
            Exception: 当数据库操作失败时抛出异常
        """
        permission = Permission(
            code=code,
            resource=resource,
            action=action,
            scope=scope,
            description=description
        )
        db.session.add(permission)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
        return permission

# 用户-权限直接关联表
# 这是一个关联表，用于实现用户和权限之间的多对多直接关联
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),  # 用户ID，外键关联users表
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),  # 权限ID，外键关联permissions表
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc)),  # 创建时间
    db.Column('expires_at', db.DateTime)  # 过期时间，可选
)