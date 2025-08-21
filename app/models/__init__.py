# 模型包初始化文件
# 从各个模块导入模型类，以便其他模块可以通过 app.models 直接访问

from .user.user import User
from .token import TokenBlocklist
from .report.inspection_report import InspectionReport
from .user.role import Role
from .user.permission import Permission, user_permissions
from .user.user_role import user_roles
from .announcement import Announcement

__all__ = ['User', 'TokenBlocklist', 'InspectionReport', 'Role', 'Permission', 'user_roles', 'user_permissions', 'Announcement']