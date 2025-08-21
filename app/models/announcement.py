from app.db import db
from datetime import datetime, timezone
from app.utils.user_utils import get_user_nickname

class Announcement(db.Model):
    """公告模型类
    用于存储系统中的公告信息，包括标题、内容、图标等
    """
    __tablename__ = 'announcements'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True, index=True)  # 公告ID，主键，索引
    title = db.Column(db.String(200), nullable=False, index=True)  # 公告标题，非空，索引
    content = db.Column(db.Text, nullable=False)  # 公告内容，非空
    icon = db.Column(db.String(255))  # 公告图标URL
    is_active = db.Column(db.Boolean, default=True)  # 是否激活，默认为True
    is_deleted = db.Column(db.Boolean, default=False)  # 是否删除（软删除标记），默认为False
    priority = db.Column(db.Integer, default=0)  # 优先级，数字越大优先级越高
    start_date = db.Column(db.DateTime)  # 开始显示时间
    end_date = db.Column(db.DateTime)  # 结束显示时间
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间，自动更新
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 创建人ID，外键关联users表
    created_by_nickname = db.Column(db.String(50))  # 创建人昵称或者账号



    def __repr__(self):
        """返回公告的字符串表示"""
        return f'<Announcement {self.title} (ID: {self.id})>'

    def to_dict(self):
        """将模型转换为字典格式
        返回的字典包含公告的所有关键信息，方便API返回或数据处理
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'icon': self.icon,
            'is_active': self.is_active,
            'is_deleted': self.is_deleted,
            'priority': self.priority,
            'start_date': self.start_date.strftime('%Y-%m-%d %H:%M:%S') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d %H:%M:%S') if self.end_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,  # 创建人ID
            'created_by_nickname': get_user_nickname(self.created_by) if self.created_by else '',  # 创建人昵称或者账号
        }

    def to_dict_cn(self):
        """将模型转换为中文键的字典格式"""
        data = self.to_dict()
        field_mapping = self.get_field_mapping()
        return {field_mapping.get(key, key): value for key, value in data.items()}

    @classmethod
    def get_field_mapping(cls):
        """获取字段名到中文的映射字典"""
        return {
            'id': 'ID',
            'title': '公告标题',
            'content': '公告内容',
            'icon': '公告图标',
            'is_active': '是否激活',
            'is_deleted': '是否删除',
            'priority': '优先级',
            'start_date': '开始显示时间',
            'end_date': '结束显示时间',
            'created_at': '创建时间',
            'updated_at': '更新时间',
            'created_by': '创建人'
        }