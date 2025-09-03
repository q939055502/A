from app import mail
import uuid
import random
import string
from datetime import datetime, timezone, timedelta

# 延迟导入db以避免循环依赖问题
from app.db import db
from app.utils.date_time import datetime_to_string
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from flask_mail import Message
from app.utils.logger import logger
from app.models.user.role import Role
from app.models.user.permission import user_permissions
from app.models.user.user_role import user_roles

class User(db.Model):
    __tablename__ = 'users'  # 明确指定表名

    # 基础身份标识字段
    id = db.Column(db.Integer, primary_key=True, index=True)  # 用户唯一ID，关联其他表的核心标识
    username = db.Column(db.String(50), unique=True, index=True, nullable=False)  # 登录用户名，唯一不可重复
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)  # 邮箱地址，用于登录、找回密码
    phone_number = db.Column(db.String(20), unique=True, index=True)  # 手机号，替代邮箱作为登录凭证

    # 认证与安全字段
    password_hash = db.Column(db.String(255), nullable=False)  # 加密后的密码，绝不存明文

    # 个人资料字段
    nickname = db.Column(db.String(50))  # 用户昵称，显示用
    avatar = db.Column(db.String(255))  # 头像图片URL地址
    gender = db.Column(db.Integer)  # 性别（0-未知、1-男、2-女）
    birthday = db.Column(db.Date)  # 出生日期，用于年龄计算
    address = db.Column(db.Text)  # 用户地址，如默认收货地址
    bio = db.Column(db.Text)  # 个人简介，社交平台常用

    # 状态与权限字段
    status = db.Column(db.Integer, default=1)  # 账号状态（0-删除、1-正常、2-禁用）
    
    # 关系映射
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'),
                           foreign_keys=[user_roles.c.user_id, user_roles.c.role_id])
    permissions = db.relationship('Permission', secondary=user_permissions, backref=db.backref('users', lazy='dynamic'))

    # 时间与跟踪字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 账号创建时间，不允许修改
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 账号信息最后更新时间
    last_login_at = db.Column(db.DateTime)  # 最后一次登录时间，用于安全审计
    last_logout_at = db.Column(db.DateTime)  # 最后一次注销时间，用于安全审计
    deleted_at = db.Column(db.DateTime)  # 软删除标记，便于恢复

    # 扩展字段
    openid = db.Column(db.String(64))  # 第三方登录标识（微信、QQ等）
    unionid = db.Column(db.String(64))  # 第三方登录联合标识
    member_level = db.Column(db.Integer, default=1)  # 会员等级，区分权益
    ext_info = db.Column(db.JSON)  # 存储扩展信息，避免频繁修改表结构

    # 岗位与职业信息
    position_name = db.Column(db.String(100))  # 岗位名称
    employment_type = db.Column(db.Integer)  # 雇佣类型（1-全职、2-兼职、3-实习）
    hire_date = db.Column(db.DateTime)  # 入职日期
    department_id = db.Column(db.Integer)  # 部门ID

    # 敏感信息（加密存储）
    id_card_number = db.Column(db.String(128))  # 身份证号（加密存储）

    # 密码重置相关字段
    reset_token = db.Column(db.String(128))  # 密码重置令牌
    reset_token_expires = db.Column(db.DateTime)  # 密码重置令牌过期时间
    verification_code = db.Column(db.String(10))  # 邮箱验证码
    verification_code_expires = db.Column(db.DateTime)  # 验证码过期时间

    # 关系映射
    #inspections = db.relationship('Inspection', backref='user', lazy=True)
    # 其他关系映射...



    
    def __repr__(self):
        return f'<User {self.username} (ID: {self.id})>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        # 直接使用明文身份证号
        id_card_number = self.id_card_number

        return {
            'id': self.id,  # 用户唯一标识符
            'username': self.username,  # 用户名
            'email': self.email,  # 电子邮箱
            'phone_number': self.phone_number,  # 电话号码
            'nickname': self.nickname,  # 昵称
            'avatar': self.avatar,  # 头像URL/路径
            'gender': self.gender,  # 性别
            'birthday': datetime_to_string(datetime.combine(self.birthday, datetime.min.time()), '%Y-%m-%d') if self.birthday else None,  # 生日，格式化输出
            'address': self.address,  # 地址
            'bio': self.bio,  # 个人简介
            'status': self.status,  # 账号状态(激活/禁用等)
            'position_name': self.position_name,  # 岗位名称
            'employment_type': self.employment_type,  # 雇佣类型
            'hire_date': datetime_to_string(self.hire_date, '%Y-%m-%d') if self.hire_date else None,  # 入职日期
            'department_id': self.department_id,  # 部门ID
            'created_at': datetime_to_string(self.created_at, '%Y-%m-%d %H:%M:%S') if self.created_at else None,  # 创建时间，格式化输出
            'updated_at': datetime_to_string(self.updated_at, '%Y-%m-%d %H:%M:%S') if self.updated_at else None,  # 更新时间，格式化输出
            'last_login_at': datetime_to_string(self.last_login_at, '%Y-%m-%d %H:%M:%S') if self.last_login_at else None,  # 最后登录时间，格式化输出
            'member_level': self.member_level,  # 会员等级
            'ext_info': self.ext_info,  # 扩展信息
            # 返回处理后的身份证号
            'id_card_number': id_card_number
        }

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        
    def update_profile(self, nickname=None, phone_number=None, avatar=None, address=None, bio=None, position_name=None, employment_type=None, hire_date=None, department_id=None, gender=None, birthday=None, ext_info=None):
        """更新用户资料

        Args:
            nickname (str, optional): 昵称
            phone_number (str, optional): 电话号码
            avatar (str, optional): 头像URL
            address (str, optional): 地址
            bio (str, optional): 个人简介
            position_name (str, optional): 岗位名称
            employment_type (int, optional): 雇佣类型
            hire_date (datetime, optional): 入职日期
            department_id (int, optional): 部门ID

        Returns:
            User: 更新后的用户对象
        """
        # 条件更新用户昵称（仅当提供新值时）
        if nickname is not None:
            self.nickname = nickname
        # 条件更新用户电话（仅当提供新值时）
        if phone_number is not None:
            self.phone_number = phone_number
        # 条件更新用户头像（仅当提供新值时）
        if avatar is not None:
            self.avatar = avatar
        # 条件更新用户地址（仅当提供新值时）
        if address is not None:
            self.address = address
        # 条件更新用户简介（仅当提供新值时）
        if bio is not None:
            self.bio = bio
        # 条件更新岗位名称（仅当提供新值时）
        if position_name is not None:
            self.position_name = position_name
        # 条件更新雇佣类型（仅当提供新值时）
        if employment_type is not None:
            self.employment_type = employment_type
        # 条件更新入职日期（仅当提供新值时）
        if hire_date is not None:
            self.hire_date = hire_date
        # 条件更新部门ID（仅当提供新值时）
        if department_id is not None:
            self.department_id = department_id
        # 条件更新性别（仅当提供新值时）
        if gender is not None:
            self.gender = gender
        # 条件更新出生日期（仅当提供新值时）
        if birthday is not None:
            self.birthday = birthday
        # 条件更新扩展信息（仅当提供新值时）
        if ext_info is not None:
            self.ext_info = ext_info
        # 更新最后修改时间为当前UTC时间
        self.updated_at = datetime.now(timezone.utc)
        # 提交数据库会话，保存更改
        db.session.commit()
        # 返回更新后的用户对象
        return self

    def update_sensitive_info(self, id_card_number=None):
        """更新用户敏感信息

        Args:
            id_card_number (str, optional): 身份证号（明文存储）

        Returns:
            User: 更新后的用户对象
        """
        # 条件更新身份证号（仅当提供新值时）
        if id_card_number is not None:
            # 明文存储身份证号
            self.id_card_number = id_card_number
        # 更新最后修改时间为当前UTC时间
        self.updated_at = datetime.now(timezone.utc)
        # 提交数据库会话，保存更改
        db.session.commit()
        # 返回更新后的用户对象
        return self

    def get_education_records(self):
        """获取用户的所有教育经历

        Returns:
            list: 教育经历列表
        """
        from app.models.user.education import Education
        return Education.query.filter_by(user_id=self.id).all()

    def get_certificates(self):
        """获取用户的所有证书

        Returns:
            list: 证书列表
        """
        from app.models.user.certificate import Certificate
        return Certificate.query.filter_by(user_id=self.id).all()

    def get_department(self):
        """获取用户所属部门信息

        Returns:
            Department: 部门对象，如不存在则返回None
        """
        # 假设存在Department模型
        try:
            from app.models.department import Department
            if self.department_id:
                return Department.query.get(self.department_id)
            return None
        except ImportError:
            logger.warning("Department model not found")
            return None

    
    
    def soft_delete(self):
        # 软删除用户
        self.status = 0  # 标记为禁用
        self.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return self


    
    def restore(self):
        # 恢复用户
        self.status = 1  # 标记为正常
        self.deleted_at = None
        db.session.commit()
        return self

    def generate_verification_token(self):
        # 生成邮箱验证令牌
        return str(uuid.uuid4())

    @staticmethod
    def generate_verification_code(length=6):
        """生成指定长度的数字验证码

        Args:
            length (int): 验证码长度

        Returns:
            str: 数字验证码
        """
        return ''.join(random.choices(string.digits, k=length))

    def generate_reset_token(self):
        # 生成唯一令牌
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        return self.reset_token

    def reset_password(self, token, new_password):
        # 验证令牌并更新密码
        if self.reset_token == token and self.reset_token_expires > datetime.now(timezone.utc):
            self.set_password(new_password)
            self.reset_token = None
            self.reset_token_expires = None
            db.session.commit()
            return True
        return False

    @classmethod
    def get_by_username(cls, username):
        
        user = cls.query.filter_by(username=username).first()
        logger.debug(f"通过用户名 {username} 查询用户: {user}")
        return user

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_active_users(cls):
        return cls.query.filter_by(status=1, deleted_at=None).all()




def send_verification_email(recipient, code):
    """发送验证码邮件

    Args:
        recipient: 用户对象或邮箱字符串
        code: 验证码字符串

    Returns:
        tuple: (success, message)
    """
    try:
        from app import mail
        from flask_mail import Message
        from app.utils.logger import logger
        import os

        # 确定收件人邮箱
        if isinstance(recipient, User):
            email = recipient.email
            username = recipient.username
        else:
            email = recipient
            username = '用户'

        # 创建邮件消息
        msg = Message('邮箱验证码', recipients=[email])
        msg.body = f'亲爱的{username}，您的邮箱验证码是：{code}。\n\n此验证码有效期为5分钟，请尽快完成验证。\n\n请勿将验证码泄露给他人。'

        # 检查是否为测试模式或开发环境，不实际发送邮件
        test_mode = os.environ.get('TEST_MODE', '0') == '1'
        dev_env = os.environ.get('FLASK_ENV') == 'development'

        if test_mode or dev_env:
            # 在测试模式或开发环境下，打印验证码已移除
            # print(f'===== 测试验证码: {code} =====')
            logger.debug(f'测试/开发环境下模拟发送邮件到 {email}: {msg.body}')
            return True, f'测试/开发环境下邮件已模拟发送，验证码: {code}'
        # 环境变量测试打印已移除
        # print(test_mode)
        # print(dev_env)
        # print('-----------------------------------------------------   ')


        # 生产环境下实际发送邮件
        mail.send(msg)
        # logger.info(f'邮件已成功发送到 {email}')
        return True, f'邮件已成功发送到 {email}'
    except Exception as e:
        logger.error(f'发送邮件失败: {str(e)}')
        return False, f'发送邮件失败: {str(e)}'








    
    