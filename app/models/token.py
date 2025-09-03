from datetime import datetime, timezone
from app import db

class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'  # 明确指定表名，确保与数据库一致
    # 下次迁移  新建字段区分 access_token和refresh_token
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))