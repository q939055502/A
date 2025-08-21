from datetime import datetime, timezone
from app.db import db
from app.models.user.user import User

class Certificate(db.Model):
    __tablename__ = 'certificates'  # 明确指定表名

    id = db.Column(db.Integer, primary_key=True, index=True)  # 主键ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 关联用户ID
    certificate_name = db.Column(db.String(200), nullable=False)  # 证书全称
    issuing_authority = db.Column(db.String(200), nullable=False)  # 发证机构
    issue_date = db.Column(db.DateTime, nullable=False)  # 颁发日期
    expiry_date = db.Column(db.DateTime)  # 有效期至（可为空，表示长期有效）
    certificate_number = db.Column(db.String(100))  # 证书编号
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间

    # 关系映射
    user = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))

    def __repr__(self):
        return f'<Certificate {self.certificate_name} (User ID: {self.user_id})>'

    def to_dict(self):
        from app.utils.date_time import datetime_to_string
        return {
            'id': self.id,
            'user_id': self.user_id,
            'certificate_name': self.certificate_name,
            'issuing_authority': self.issuing_authority,
            'issue_date': datetime_to_string(self.issue_date, '%Y-%m-%d') if self.issue_date else None,
            'expiry_date': datetime_to_string(self.expiry_date, '%Y-%m-%d') if self.expiry_date else None,
            'certificate_number': self.certificate_number,
            'created_at': datetime_to_string(self.created_at, '%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': datetime_to_string(self.updated_at, '%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }