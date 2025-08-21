from datetime import datetime, timezone
from app.db import db
from app.models.user.user import User

class Education(db.Model):
    __tablename__ = 'educations'  # 明确指定表名

    id = db.Column(db.Integer, primary_key=True, index=True)  # 主键ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 关联用户ID
    education_level = db.Column(db.Integer, nullable=False)  # 学历层次（1-小学、2-初中、3-高中、4-专科、5-本科、6-硕士、7-博士）
    school_name = db.Column(db.String(200), nullable=False)  # 毕业院校
    major = db.Column(db.String(100), nullable=False)  # 专业
    graduation_date = db.Column(db.DateTime, nullable=False)  # 毕业日期
    degree_certificate_number = db.Column(db.String(100))  # 学位证书编号
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 更新时间

    # 关系映射
    user = db.relationship('User', backref=db.backref('educations', lazy='dynamic'))

    def __repr__(self):
        return f'<Education {self.school_name} - {self.major} (User ID: {self.user_id})>'

    def to_dict(self):
        from app.utils.date_time import datetime_to_string
        return {
            'id': self.id,
            'user_id': self.user_id,
            'education_level': self.education_level,
            'school_name': self.school_name,
            'major': self.major,
            'graduation_date': datetime_to_string(self.graduation_date, '%Y-%m-%d') if self.graduation_date else None,
            'degree_certificate_number': self.degree_certificate_number,
            'created_at': datetime_to_string(self.created_at, '%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': datetime_to_string(self.updated_at, '%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }