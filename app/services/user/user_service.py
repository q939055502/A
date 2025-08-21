# 用户业务逻辑服务
import re
import random
import time
import redis
import os
import uuid
from app.utils.jwt import generate_tokens
from app.models.user.user import User
from app import db, mail
from flask_mail import Message
import logging
from datetime import timedelta, datetime, timezone
from app.utils.logger import logger
from app.utils.response import api_response
from app.utils.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
REDIS_DB = int(os.environ.get('REDIS_DB') or 0)

# 创建Redis客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# 邮箱验证码过期时间（秒）
EMAIL_CODE_EXPIRE = 300

# 邮箱发送间隔（秒）
EMAIL_SEND_INTERVAL = 60

# 内存存储，用于Redis不可用的情况
email_memory_storage = {}

class UserService:

    @staticmethod
    def verify_login_status():
        """验证用户登录状态

        Returns:
            tuple: (Flask响应对象, HTTP状态码)
        """
        from flask_jwt_extended import get_jwt_identity
        from app.utils.response import api_response
        from app.utils.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED
        from app.models.user.user import User

        # 直接获取当前用户标识
        current_user = get_jwt_identity()
        if current_user:
            # 用户已登录，获取用户对象
            user = User.query.get(current_user)
            if user:
                user.update_last_login()
                return api_response(
                    success=True,
                    code=HTTP_200_OK,
                    message="登录状态验证成功",
                    data={
                        "is_authenticated": True,
                        "user": user.to_dict()
                    }
                )
        # 用户未登录或令牌无效
        return api_response(
            success=False,
            code=HTTP_401_UNAUTHORIZED,
            message="用户未登录或令牌无效",
            data={
                "is_authenticated": False
            }
        )

    @staticmethod
    def logout(user_id, access_token=None, refresh_token=None):
        """用户注销方法

        Args:
            user_id (int): 用户ID
            access_token (str, optional): 用户当前使用的访问令牌
            refresh_token (str, optional): 用户当前使用的刷新令牌

        Returns:
            tuple: (是否成功, 消息)
        """
        from app.utils.jwt import process_logout_token
        from app.utils.logger import logger

        try:
            # 查找用户
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"注销失败：用户ID {user_id} 不存在")
                return False, '用户不存在'

            # 记录注销时间
            user.last_logout_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)

            # 如果提供了令牌，将其添加到黑名单
            if access_token:
                success = process_logout_token(access_token)
                if not success:
                    logger.warning(f"将访问令牌加入黑名单失败")
            if refresh_token:
                success = process_logout_token(refresh_token)
                if not success:
                    logger.warning(f"将刷新令牌加入黑名单失败")

            # 提交数据库会话，保存更改
            db.session.commit()
            logger.info(f"用户 {user.username} (ID: {user_id}) 注销成功")
            return True, '注销成功'
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户注销过程中出错: {str(e)}")
            return False, f'注销失败: {str(e)}'

    @staticmethod
    def update_user_profile(user_id, data):
        """更新用户资料

        Args:
            user_id (int): 用户ID
            data (dict): 包含要更新的用户资料的字典

        Returns:
            tuple: (是否成功, 消息)
        """
        # 查找用户
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"更新用户资料失败：用户ID {user_id} 不存在")
            return False, '用户不存在'

        # 定义允许更新的字段
        allowed_fields = [
            'nickname', 'phone_number', 'avatar', 'gender',
            'birthday', 'address', 'bio', 'ext_info'
        ]

        # 定义需要特殊处理的字段验证
        validation_rules = {
            'gender': lambda x: isinstance(x, int) and x in [0, 1, 2],
            'phone_number': lambda x: re.match(r'^1[3-9]\d{9}$', x) if x else True
        }

        # 更新字段
        try:
            for field, value in data.items():
                # 检查是否为允许更新的字段
                if field not in allowed_fields:
                    logger.warning(f"更新用户资料失败：字段 {field} 不允许更新")
                    return False, f'不允许更新字段: {field}'

                # 检查是否有特殊验证规则
                if field in validation_rules and not validation_rules[field](value):
                    logger.warning(f"更新用户资料失败：字段 {field} 格式不正确")
                    if field == 'gender':
                        return False, '性别必须是0(未知)、1(男)或2(女)'
                    elif field == 'phone_number':
                        return False, '手机号格式不正确'

                # 避免空指针，只在值不为None时更新
                if value is not None:
                    setattr(user, field, value)

            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"用户 {user.username} (ID: {user.id}) 资料更新成功")
            return True, '资料更新成功'
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户 {user.username} (ID: {user.id}) 资料更新失败: {str(e)}")
            return False, f'资料更新失败: {str(e)}'

    @staticmethod
    def get_user_info(user_id):
        """获取用户详细信息
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            tuple: (是否成功, 用户数据或错误消息)
        """
        try:
            # 查询用户
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"获取用户信息失败：用户ID {user_id} 不存在")
                return False, '用户不存在'
            
            # 使用user对象的to_dict方法获取用户数据
            user_data = user.to_dict()
            
            # 获取用户的角色和权限信息（包括直接拥有和通过角色获得的权限）
            from app.services.permission_service import PermissionService
            roles_and_permissions = PermissionService.get_roles_and_permissions(user)
            user_data['roles'] = roles_and_permissions['roles']
            user_data['permissions'] = roles_and_permissions['permissions']
            
            logger.info(f"获取用户 {user.username} (ID: {user_id}) 信息成功")
            return True, user_data
        except Exception as e:
            logger.error(f"获取用户信息时出错: {str(e)}")
            return False, f'获取用户信息失败: {str(e)}'





            
    @staticmethod
    def is_redis_available():
        """检查Redis连接状态"""
        try:
            return redis_client.ping()
        except:
            return False

    @staticmethod
    def generate_email_code(length=6):
        """生成指定长度的数字验证码"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    

    @staticmethod
    def register_user(data):
        """注册新用户

        Args:
            data (dict): 包含用户注册信息的字典

        Returns:
            tuple: (用户对象或None, 错误信息或None)
        """
        is_valid, error = UserService.validate_registration(data)
        if not is_valid:
            return None, error
        
        try:
            new_user = User(
                username=data.get('username'),
                email=data.get('email'),
                nickname=data.get('nickname') or data.get('username')
            )
            new_user.set_password(data.get('password'))  # 使用set_password方法加密密码
            db.session.add(new_user)
            
            db.session.commit()
            
            return new_user, None
        except Exception as e:
            db.session.rollback()
            logging.error(f"注册用户失败: {str(e)}")
            return None, f'注册失败: {str(e)}'

    @staticmethod
    def assign_user_role_and_permissions(user):
        """为新用户分配角色和权限

        Args:
            user (User): 用户对象

        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        try:
            from app.models.user.role import Role
            from app.models.user.permission import Permission
            from app.services.permission_service import PermissionService

            # 获取普通用户角色
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                # 如果普通用户角色不存在，创建它
                user_role = Role(name='user', description='普通用户角色')
                db.session.add(user_role)

            # 分配角色
            if user_role not in user.roles:
                user.roles.append(user_role)

            # 确保用户拥有编辑自己信息的权限
            edit_own_info_perm = Permission.query.filter_by(
                resource='user',
                action='edit',
                scope='own'
            ).first()

            if not edit_own_info_perm:
                # 如果权限不存在，创建它
                edit_own_info_perm = Permission(
                    code='user:edit:own',
                    resource='user',
                    action='edit',
                    scope='own',
                    description='编辑自己的用户信息'
                )
                db.session.add(edit_own_info_perm)

            # 直接分配权限给用户
            if edit_own_info_perm not in user.permissions:
                user.permissions.append(edit_own_info_perm)

            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            logger.error(f"为用户分配角色和权限失败: {str(e)}")
            return False, f'分配角色和权限失败: {str(e)}'



    @staticmethod
    def authenticate_user(username, password):
        """验证用户身份

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            tuple: (用户对象或None, 错误信息或None)
        """
        user = User.query.filter_by(username=username).first()
        if not user:
            return None, '用户不存在'

        if not user.check_password(password):
            return None, '密码错误'

        return user, None

    @staticmethod
    def login(username, password, remember_me=False, request_id=None):
        """用户登录方法

        Args:
            username (str): 用户名或邮箱
            password (str): 密码
            remember_me (bool, optional): 是否记住我. Defaults to False.
            request_id (str, optional): 请求ID. Defaults to None.

        Returns:
            tuple: (user, access_token, refresh_token, request_id, error_message)
        """
        user = None
        access_token = None
        refresh_token = None
        error = None
        try:
            # 尝试通过用户名或邮箱查找用户
            user = User.get_by_username(username) or User.get_by_email(username)
            logger.info(f"登录验证: 查找用户结果={user is not None}")
            # 验证用户是否存在且密码正确
            if not user or not user.check_password(password):
                error = "用户名或密码错误"
                logger.warning(f"登录失败: {error}")
            elif user.status != 1:
                # 验证用户状态
                error = "账号状态异常，请联系管理员"
                logger.warning(f"登录失败: {error}, 用户状态={user.status}")
            else:
                # 生成令牌
                logger.info(f"开始生成令牌: 用户ID={user.id}, remember_me={remember_me}, 类型={type(remember_me)}")
                try:
                    access_token, refresh_token = generate_tokens(user.id, remember_me)
                    logger.info(f"令牌生成结果: access_token={access_token is not None}, refresh_token={refresh_token is not None}")
                    logger.info(f"令牌过期时间设置: remember_me={remember_me}, 刷新令牌过期时间={'7天' if remember_me else '1天'}")
                except Exception as e:
                    logger.error(f"令牌生成失败: {str(e)}, 用户ID={user.id}, remember_me={remember_me}")
                    raise

                # 更新最后登录时间
                user.update_last_login()
        except Exception as e:
            logger.error(f"登录过程中出错: {str(e)}")
            error = f"登录失败: {str(e)}"
        logger.info(f"登录方法返回: user={user is not None}, error={error}")
        return user, access_token, refresh_token, request_id, error











    @staticmethod
    def verify_email_code(email, code, code_type='register'):
        """验证邮箱验证码

        Args:
            email (str): 用户邮箱
            code (str): 验证码
            code_type (str): 验证码类型，默认为'register'（注册），可选'reset_password'（重置密码）

        Returns:
            tuple: (是否成功, 消息)
        """
        redis_available = UserService.is_redis_available()
        stored_code = None
        stored_time = None

        # 根据验证码类型构建存储键
        code_key = f'email:{code_type}:code:{email}'
        time_key = f'email:{code_type}:code_time:{email}'
        last_send_key = f'email:{code_type}:last_send_time:{email}'

        if redis_available:
            # 从Redis获取验证码
            stored_code = redis_client.get(code_key)
            stored_time = redis_client.get(time_key)
        else:
            # 从内存存储获取验证码
            if email in email_memory_storage and code_type in email_memory_storage[email]:
                stored_code = email_memory_storage[email][code_type]['code']
                stored_time = email_memory_storage[email][code_type]['code_time']

        # 检查验证码是否存在
        if not stored_code:
            return False, f'{code_type == "register" and "注册" or "重置密码"}验证码不存在或已过期'

        # 检查验证码是否过期
        if float(stored_time) + EMAIL_CODE_EXPIRE < time.time():
            # 清理过期验证码
            if redis_available:
                redis_client.delete(code_key)
                redis_client.delete(time_key)
            else:
                if email in email_memory_storage and code_type in email_memory_storage[email]:
                    del email_memory_storage[email][code_type]
            return False, f'{code_type == "register" and "注册" or "重置密码"}验证码已过期'

        # 验证验证码
        if stored_code != code:
            return False, f'{code_type == "register" and "注册" or "重置密码"}验证码不正确'

        # 验证成功，清理验证码
        if redis_available:
            redis_client.delete(code_key)
            redis_client.delete(time_key)
        else:
            if email in email_memory_storage and code_type in email_memory_storage[email]:
                del email_memory_storage[email][code_type]

        return True, f'{code_type == "register" and "注册" or "重置密码"}验证码验证成功'

    @staticmethod
    def send_email_code(email, code_type='register', check_user_exists=True):
        """发送邮箱验证码

        Args:
            email (str): 用户邮箱
            code_type (str): 验证码类型，默认为'register'（注册），可选'reset_password'（重置密码）
            check_user_exists (bool): 是否检查用户存在，默认为True

        Returns:
            tuple: (是否成功, 消息)
        """
        # 检查是否在发送间隔内
        redis_available = UserService.is_redis_available()
        last_send_time = None

        # 根据验证码类型构建存储键
        code_key = f'email:{code_type}:code:{email}'
        time_key = f'email:{code_type}:code_time:{email}'
        last_send_key = f'email:{code_type}:last_send_time:{email}'

        if redis_available:
            last_send_time = redis_client.get(last_send_key)
        else:
            # 使用内存存储检查发送间隔
            if email in email_memory_storage and code_type in email_memory_storage[email]:
                last_send_time = email_memory_storage[email][code_type]['last_send_time']

        if last_send_time and float(last_send_time) + EMAIL_SEND_INTERVAL > time.time():
            remaining_time = int(float(last_send_time) + EMAIL_SEND_INTERVAL - time.time())
            return False, f'{code_type == "register" and "注册" or "重置密码"}验证码发送过于频繁，请 {remaining_time} 秒后再试'

        # 生成验证码
        code = UserService.generate_email_code()
        logger.info(f'生成{code_type == "register" and "注册" or "重置密码"}验证码: {code}')

        # 存储验证码
        current_time = time.time()
        if redis_available:
            # 存储到Redis
            redis_client.set(code_key, code, ex=EMAIL_CODE_EXPIRE)
            redis_client.set(last_send_key, str(current_time))
            # 同时存储code_time以兼容verify_email_code函数
            redis_client.set(time_key, str(current_time), ex=EMAIL_CODE_EXPIRE)
        else:
            # 存储到内存
            if email not in email_memory_storage:
                email_memory_storage[email] = {}
            if code_type not in email_memory_storage[email]:
                email_memory_storage[email][code_type] = {}
            email_memory_storage[email][code_type]['code'] = code
            email_memory_storage[email][code_type]['expire_time'] = current_time + EMAIL_CODE_EXPIRE
            email_memory_storage[email][code_type]['last_send_time'] = current_time
            # 同时存储code_time以兼容verify_email_code函数
            email_memory_storage[email][code_type]['code_time'] = current_time

        # 发送验证邮件
        print(f'向邮箱 {email} 发送{code_type == "register" and "注册" or "重置密码"}验证码: {code}')
        logger.info(f'准备向邮箱 {email} 发送{code_type == "register" and "注册" or "重置密码"}验证码: {code}')

        # 开发环境下仅打印验证码，不发送实际邮件
        if os.environ.get('FLASK_ENV') == 'development':
            logger.info(f'开发环境下仅打印{code_type == "register" and "注册" or "重置密码"}验证码: {code}，未发送实际邮件')
            return True, code

        # 生产环境调用实际的邮件发送函数
        if check_user_exists:
            user = User.query.filter_by(email=email).first()
            if user:
                logger.info(f'找到用户: {user.username} ({user.email})')
                success, message = UserService.send_verification_email(user, code, code_type)
                if success:
                    logger.info(f'{code_type == "register" and "注册" or "重置密码"}验证码邮件发送成功: {message}')
                else:
                    logger.error(f'发送邮件失败: {message}')
                    return False, message
            else:
                logger.error(f'未找到邮箱为 {email} 的用户')
                return False, '未找到该邮箱对应的用户'
        else:
            # 不检查用户存在，直接发送邮件
            success, message = UserService.send_verification_email(email, code, code_type)
            if success:
                logger.info(f'{code_type == "register" and "注册" or "重置密码"}验证码邮件发送成功: {message}')
            else:
                logger.error(f'发送邮件失败: {message}')
                return False, message

        return True, code

    @staticmethod
    def send_verification_email(recipient, code, code_type='register'):
        """发送验证邮件

        Args:
            recipient (str or User): 收件人邮箱或用户对象
            code (str): 验证码或重置令牌
            code_type (str): 邮件类型，默认为'register'（注册），可选'reset_password'（重置密码）

        Returns:
            tuple: (是否成功, 消息)
        """
        try:
            # 确定收件人邮箱和用户名
            if isinstance(recipient, User):
                email = recipient.email
                username = recipient.username
            else:
                email = recipient
                username = '用户'

            # 根据邮件类型设置主题和内容
            if code_type == 'register':
                subject = '注册邮箱验证码'
                body = f'亲爱的{username}，您的注册邮箱验证码是：{code}。\n\n此验证码有效期为5分钟，请尽快完成注册验证。\n\n请勿将验证码泄露给他人。'
            elif code_type == 'reset_password':
                subject = '密码重置验证码'
                body = f'亲爱的{username}，您的密码重置验证码是：{code}。\n\n此验证码有效期为5分钟，请尽快完成密码重置。\n\n请勿将验证码泄露给他人。'
            else:
                subject = '邮箱验证码'
                body = f'亲爱的{username}，您的邮箱验证码是：{code}。\n\n此验证码有效期为5分钟，请尽快完成验证。\n\n请勿将验证码泄露给他人。'

            # 创建邮件消息
            msg = Message(subject, recipients=[email])
            msg.body = body

            # 检查是否为测试模式或开发环境，不实际发送邮件
            test_mode = os.environ.get('TEST_MODE', '0') == '1'
            dev_env = os.environ.get('FLASK_ENV') == 'development'

            if test_mode or dev_env:
                # 在测试模式或开发环境下，打印验证码
                print(f'===== {code_type == "register" and "注册" or "重置密码"}测试验证码: {code} =====')
                logger.info(f'测试/开发环境下模拟发送{code_type == "register" and "注册" or "重置密码"}邮件到 {email}: {msg.body}')
                return True, f'测试/开发环境下邮件已模拟发送，验证码: {code}'

            # 生产环境下实际发送邮件
            mail.send(msg)
            return True, f'邮件已成功发送到 {email}'
        except Exception as e:
            logger.error(f'发送邮件失败: {str(e)}')
            return False, f'发送邮件失败: {str(e)}'

    @staticmethod
    def validate_registration(data):
        """验证用户注册信息

        Args:
            data (dict): 包含用户注册信息的字典

        Returns:
            tuple: (是否有效, 错误信息或None)
        """
        # 验证用户名
        if not data.get('username'):
            return False, '用户名不能为空'
        if len(data.get('username')) < 3 or len(data.get('username')) > 20:
            return False, '用户名长度必须在3-20个字符之间'
        if not re.match(r'^[a-zA-Z0-9_]+$', data.get('username')):
            return False, '用户名只能包含字母、数字和下划线'

        # 验证密码
        if not data.get('password'):
            return False, '密码不能为空'
        if len(data.get('password')) < 6:
            return False, '密码长度不能少于6个字符'
        if not re.search(r'[A-Za-z]', data.get('password')) or not re.search(r'[0-9]', data.get('password')):
            return False, '密码必须包含字母和数字'

        # 验证邮箱
        if data.get('email') and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', data.get('email')):
            return False, '邮箱格式不正确'

        # 检查用户名是否已存在
        if User.query.filter_by(username=data.get('username')).first():
            return False, '用户名已存在'

        return True, None


    @staticmethod
    def generate_password_reset_token_and_send_email(email):
        """生成密码重置令牌并发送邮件

        Args:
            email (str): 用户邮箱

        Returns:
            tuple: (是否成功, 消息)
        """
        # 检查用户是否存在
        user = User.get_by_email(email)
        if not user:
            logger.warning(f"密码重置请求失败：邮箱 {email} 未注册")
            return False, '未找到该邮箱对应的用户'

        # 生成重置令牌
        reset_token = str(uuid.uuid4())
        user.reset_token = reset_token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        logger.info(f"为用户 {user.username} (ID: {user.id}) 生成密码重置令牌")

        # 发送重置邮件
        success, message = UserService.send_verification_email(user, reset_token)
        if success:
            logger.info(f"密码重置邮件发送成功：用户 {user.username} (ID: {user.id})")
            return True, '密码重置链接已发送到您的邮箱，请在24小时内完成重置'
        else:
            logger.error(f"密码重置邮件发送失败：用户 {user.username} (ID: {user.id}), 错误: {message}")
            return False, f'发送密码重置邮件失败: {message}'

    @staticmethod
    def reset_user_password(token, new_password):
        """验证重置令牌并重置密码

        Args:
            token (str): 密码重置令牌
            new_password (str): 新密码

        Returns:
            tuple: (是否成功, 消息)
        """
        # 查找拥有该重置令牌的用户
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            logger.warning(f"密码重置失败：无效的重置令牌 {token}")
            return False, '无效的密码重置令牌'

        # 检查令牌是否过期
        if user.reset_token_expires < datetime.now(timezone.utc):
            logger.warning(f"密码重置失败：令牌 {token} 已过期")
            return False, '密码重置令牌已过期，请重新申请'

        # 验证新密码
        if len(new_password) < 6:
            return False, '密码长度不能少于6个字符'
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'[0-9]', new_password):
            return False, '密码必须包含字母和数字'

        # 重置密码
        try:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            logger.info(f"用户 {user.username} (ID: {user.id}) 密码重置成功")
            return True, '密码重置成功，请使用新密码登录'
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户 {user.username} (ID: {user.id}) 密码重置失败: {str(e)}")
            return False, f'密码重置失败: {str(e)}'





    @staticmethod
    def reset_password_by_email_code(email, new_password):
        """通过邮箱验证码重置密码

        Args:
            email (str): 用户邮箱
            new_password (str): 新密码

        Returns:
            tuple: (是否成功, 消息)
        """
        # 查找用户
        user = User.get_by_email(email)
        if not user:
            logger.warning(f"密码重置请求失败：邮箱 {email} 未注册")
            return False, '未找到该邮箱对应的用户'

        # 验证新密码
        if len(new_password) < 6:
            return False, '密码长度不能少于6个字符'
        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'[0-9]', new_password):
            return False, '密码必须包含字母和数字'

        # 重置密码
        try:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            logger.info(f"用户 {user.username} (ID: {user.id}) 通过邮箱验证码重置密码成功")
            return True, '密码重置成功，请使用新密码登录'
        except Exception as e:
            db.session.rollback()
            logger.error(f"用户 {user.username} (ID: {user.id}) 通过邮箱验证码重置密码失败: {str(e)}")
            return False, f'密码重置失败: {str(e)}'

    

