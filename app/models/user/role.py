import uuid
from app.db import db  # 导入数据库实例
from datetime import datetime, timezone  # 导入日期时间相关模块

# 角色-权限关联表
# 这是一个关联表，用于实现角色和权限之间的多对多关系
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),  # 角色ID，外键关联roles表
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),  # 权限ID，外键关联permissions表
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc)),  # 创建时间
    db.Column('created_by', db.Integer, db.ForeignKey('users.id')),  # 创建人ID，外键关联users表
    db.Column('is_active', db.Boolean, default=True)  # 是否激活，默认为True
)

class Role(db.Model):
    """角色模型类
    用于表示系统中的角色，角色可以拥有多个权限，也可以有父角色
    """
    __tablename__ = 'roles'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, index=True)  # 角色ID，主键，索引
    name = db.Column(db.String(50), unique=True, index=True, nullable=False)  # 角色名称，唯一，索引，非空
    description = db.Column(db.Text)  # 角色描述
    parent_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 父角色ID，外键关联自身表
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间，自动更新
    is_active = db.Column(db.Boolean, default=True)  # 是否激活，默认为True

    # 关系定义
    parent = db.relationship('Role', remote_side=[id], backref='children')  # 父角色关系，反向引用为children
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))  # 角色拥有的权限，多对多关系

    def __repr__(self):
        """返回角色的字符串表示"""
        return f'<Role {self.name} (ID: {self.id})>'

    def get_all_permissions(self):
        """获取角色及其父角色的所有权限

        Returns:
            set: 包含所有权限对象的集合
        """
        permissions = set(self.permissions)  # 当前角色的权限
        if self.parent:  # 如果有父角色
            permissions.update(self.parent.get_all_permissions())  # 递归获取父角色的权限
        return permissions

    def get_permission_codes(self):
        """获取角色及其父角色的所有权限代码

        Returns:
            set: 包含所有权限代码的集合
        """
        codes = {permission.code for permission in self.permissions}  # 当前角色的权限代码
        if self.parent:  # 如果有父角色
            codes.update(self.parent.get_permission_codes())  # 递归获取父角色的权限代码
        return codes