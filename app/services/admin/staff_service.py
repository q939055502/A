from app import db
from app.models.user.user import User
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.models.user.user_role import user_roles
from app.models.user.permission import user_permissions
from app.utils.date_time import datetime_to_string
from app.utils.logger import logger
from app.utils.response import api_response
from app.utils.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from app.services.permission_service import PermissionService
from app.utils.schemas import StaffCreate, StaffUpdate, StaffRoleUpdate


class StaffService:
    @staticmethod
    def get_staff_list(page=1, per_page=10, keyword='', status=None, role_id=None):
        """
        获取人员列表

        Args:
            page (int): 页码
            per_page (int): 每页数量
            keyword (str): 搜索关键词
            status (int): 状态筛选
            role_id (int): 角色ID筛选

        Returns:
            tuple: (人员列表, 总数量)
        """
        try:
            query = User.query

            # 关键词筛选
            if keyword:
                query = query.filter(
                    (User.username.ilike(f'%{keyword}%')) |
                    (User.email.ilike(f'%{keyword}%')) |
                    (User.nickname.ilike(f'%{keyword}%'))
                )

            # 状态筛选
            if status is not None:
                query = query.filter(User.status == status)

            # 角色筛选
            if role_id is not None:
                query = query.join(user_roles, User.id == user_roles.c.user_id).filter(user_roles.c.role_id == role_id)

            # 排除软删除的用户
            query = query.filter(User.deleted_at.is_(None))

            # 获取总数量
            total = query.count()

            # 分页查询
            staff_list = query.order_by(User.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

            # 转换为字典列表
            staff_dicts = [staff.to_dict() for staff in staff_list]

            return staff_dicts, total
        except Exception as e:
            logger.error(f"获取人员列表失败: {str(e)}")
            raise

    @staticmethod
    def get_staff_by_id(staff_id):
        """
        根据ID获取人员

        Args:
            staff_id (int): 人员ID

        Returns:
            dict: 人员信息字典
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                return None
            return staff.to_dict()
        except Exception as e:
            logger.error(f"获取人员失败: {str(e)}")
            raise

    @staticmethod
    def create_staff(staff_data: StaffCreate):
        """
        创建新人员

        Args:
            staff_data (StaffCreate): 人员数据（已通过Pydantic验证）

        Returns:
            dict: 创建后的人员信息
        """
        data = staff_data.dict()
        try:
            # 检查用户名是否已存在
            if User.query.filter_by(username=data['username']).first():
                raise ValueError("用户名已存在")

            # 检查邮箱是否已存在
            if User.query.filter_by(email=data['email']).first():
                raise ValueError("邮箱已存在")

            # 创建新用户
            staff = User(
                username=data['username'],
                email=data['email'],
                status=data.get('status', 1)
            )
            # 设置密码
            staff.set_password(data['password'])

            # 设置其他可选字段
            if 'nickname' in data:
                staff.nickname = data['nickname']
            if 'phone_number' in data:
                staff.phone_number = data['phone_number']
            if 'avatar' in data:
                staff.avatar = data['avatar']
            if 'gender' in data:
                staff.gender = data['gender']
            if 'birthday' in data:
                staff.birthday = data['birthday']
            if 'address' in data:
                staff.address = data['address']
            if 'bio' in data:
                staff.bio = data['bio']
            if 'ext_info' in data:
                staff.ext_info = data['ext_info']
            
            # 保存到数据库
            db.session.add(staff)
            logger.info(f"准备提交用户数据: {staff.username}")
            db.session.commit()
            logger.info(f"用户数据提交成功: {staff.username}, ID: {staff.id}")

            # 提交后立即查询，验证数据是否存在
            new_staff = User.query.filter_by(username=data['username']).first()
            if new_staff:
                logger.info(f"提交后查询验证成功: {new_staff.username} 存在")
                # 如果提供了角色ID，为用户分配角色
                if 'role_ids' in data and data['role_ids']:
                    logger.info(f"为用户 {new_staff.username} 分配角色: {data['role_ids']}")
                    role_data = StaffRoleUpdate(role_ids=data['role_ids'])
                    StaffService.add_staff_roles(new_staff.id, role_data)
                    logger.info(f"角色分配成功: 用户 {new_staff.username}")
                # 尝试转换为字典并捕获可能的错误
                try:
                    staff_dict = new_staff.to_dict()
                    logger.info(f"用户数据转换成功: {new_staff.username}")
                    logger.debug(f"转换后的用户数据: {staff_dict}")
                    return staff_dict
                except Exception as e:
                    logger.error(f"转换用户数据到字典失败: {str(e)}", exc_info=True)
                    # 如果to_dict失败，返回基本信息
                    return {
                        'id': new_staff.id,
                        'username': new_staff.username,
                        'email': new_staff.email,
                        'status': new_staff.status
                    }
            else:
                logger.warning(f"提交后查询验证失败: {data['username']} 不存在")
                raise ValueError("创建用户失败，提交后未找到用户")
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建人员失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def update_staff(staff_id: int, staff_data: StaffUpdate):
        """
        更新人员信息

        Args:
            staff_id (int): 人员ID
            staff_data (StaffUpdate): 更新的数据（已通过Pydantic验证）

        Returns:
            dict: 更新后的人员信息
        """
        data = staff_data.dict(exclude_unset=True)
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 检查用户名是否已存在（如果修改了用户名）
            if 'username' in data and data['username'] != staff.username:
                if User.query.filter_by(username=data['username']).first():
                    raise ValueError("用户名已存在")
                staff.username = data['username']

            # 检查邮箱是否已存在（如果修改了邮箱）
            if 'email' in data and data['email'] != staff.email:
                if User.query.filter_by(email=data['email']).first():
                    raise ValueError("邮箱已存在")
                staff.email = data['email']

            # 更新其他字段
            if 'nickname' in data:
                staff.nickname = data['nickname']
            if 'phone_number' in data:
                staff.phone_number = data['phone_number']
            if 'avatar' in data:
                staff.avatar = data['avatar']
            if 'gender' in data:
                staff.gender = data['gender']
            if 'birthday' in data:
                staff.birthday = data['birthday']
            if 'address' in data:
                staff.address = data['address']
            if 'bio' in data:
                staff.bio = data['bio']
            if 'status' in data:
                staff.status = data['status']
            if 'ext_info' in data:
                staff.ext_info = data['ext_info']

            # 更新密码（如果提供了新密码）
            if 'password' in data and data['password']:
                staff.set_password(data['password'])

            # 保存更改（非敏感信息）
            db.session.commit()

            # 单独处理敏感信息更新
            if 'id_card_number' in data:
                staff.update_sensitive_info(id_card_number=data['id_card_number'])

            return staff.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新人员信息失败: {str(e)}")
            raise

    @staticmethod
    def delete_staff(staff_id):
        """
        删除人员
    
        Args:
            staff_id (int): 人员ID
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")
    
            # 软删除
            staff.soft_delete()
            
            # 移除重复的status设置和commit
            # staff.status = 0
            # db.session.commit()
    
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除人员失败: {str(e)}")
            raise

    @staticmethod
    def get_staff_roles(staff_id):
        """
        获取人员角色

        Args:
            staff_id (int): 人员ID

        Returns:
            list: 角色列表
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 获取用户角色
            roles = staff.roles

            # 转换为字典列表
            role_dicts = [{
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'created_at': datetime_to_string(role.created_at, '%Y-%m-%d %H:%M:%S')
            } for role in roles]

            return role_dicts
        except Exception as e:
            logger.error(f"获取人员角色失败: {str(e)}")
            raise

    @staticmethod
    def add_staff_roles(staff_id: int, role_data: StaffRoleUpdate):
        """
        添加人员角色

        Args:
            staff_id (int): 人员ID
            role_data (StaffRoleUpdate): 角色数据（已通过Pydantic验证）
        """
        role_ids = role_data.role_ids
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 验证角色是否存在
            for role_id in role_ids:
                role = Role.query.get(role_id)
                if not role:
                    raise ValueError(f"角色ID {role_id} 不存在")

            # 添加角色
            for role_id in role_ids:
                role = Role.query.get(role_id)
                if role not in staff.roles:
                    staff.roles.append(role)

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加人员角色失败: {str(e)}")
            raise

    @staticmethod
    def remove_staff_role(staff_id, role_id):
        """
        移除人员角色

        Args:
            staff_id (int): 人员ID
            role_id (int): 角色ID
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 查找角色
            role = Role.query.get(role_id)
            if not role:
                raise ValueError("角色不存在")

            # 移除角色
            if role in staff.roles:
                staff.roles.remove(role)
                db.session.commit()
            else:
                raise ValueError("该人员没有此角色")

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"移除人员角色失败: {str(e)}")
            raise

    @staticmethod
    def update_staff_roles(staff_id, role_ids):
        """
        更新人员角色（替换现有角色）

        Args:
            staff_id (int): 人员ID
            role_ids (List[int]): 角色ID列表
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 验证所有角色是否存在
            for role_id in role_ids:
                role = Role.query.get(role_id)
                if not role:
                    raise ValueError(f"角色ID {role_id} 不存在")

            # 清空现有角色
            staff.roles = []

            # 添加新角色
            for role_id in role_ids:
                role = Role.query.get(role_id)
                staff.roles.append(role)

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新人员角色失败: {str(e)}")
            raise

    @staticmethod
    def get_staff_permissions(staff_id):
        """
        获取人员权限

        Args:
            staff_id (int): 人员ID

        Returns:
            list: 权限列表
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 获取用户权限
            permissions = PermissionService.get_user_permissions(staff)

            # 转换为字典列表
            # 与User.to_dict()保持一致，不包含id字段
            permission_dicts = [{
                'code': perm.code,
                'resource': perm.resource,
                'action': perm.action,
                'scope': perm.scope,
                'description': perm.description
            } for perm in permissions]

            return permission_dicts
        except Exception as e:
            logger.error(f"获取人员权限失败: {str(e)}")
            raise

    @staticmethod
    def get_all_roles():
        """
        获取所有角色

        Returns:
            list: 角色列表
        """
        try:
            roles = Role.query.filter_by(is_active=True).all()

            # 转换为字典列表
            role_dicts = [{
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'parent_id': role.parent_id,
                'created_at': datetime_to_string(role.created_at, '%Y-%m-%d %H:%M:%S')
            } for role in roles]

            return role_dicts
        except Exception as e:
            logger.error(f"获取角色列表失败: {str(e)}")
            raise

    @staticmethod
    def create_role(data):
        """
        创建角色

        Args:
            data (dict): 角色数据

        Returns:
            dict: 创建后的角色信息
        """
        try:
            # 检查角色名称是否已存在
            if Role.query.filter_by(name=data['name']).first():
                raise ValueError("角色名称已存在")

            # 创建新角色
            role = Role(
                name=data['name'],
                description=data.get('description', ''),
                parent_id=data.get('parent_id')
            )

            # 保存到数据库
            db.session.add(role)
            db.session.commit()

            return {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'parent_id': role.parent_id,
                'created_at': datetime_to_string(role.created_at)
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建角色失败: {str(e)}")
            raise



    @staticmethod
    def update_role_permissions(role_id, add_permission_ids, remove_permission_ids):
        """
        更新角色权限（添加和移除权限）

        Args:
            role_id (int): 角色ID
            add_permission_ids (list): 要添加的权限ID列表
            remove_permission_ids (list): 要移除的权限ID列表
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                raise ValueError("角色不存在")

            # 添加权限
            for permission_id in add_permission_ids:
                permission = Permission.query.get(permission_id)
                if not permission:
                    raise ValueError(f"权限ID {permission_id} 不存在")
                if permission not in role.permissions:
                    role.permissions.append(permission)

            # 移除权限
            for permission_id in remove_permission_ids:
                permission = Permission.query.get(permission_id)
                if not permission:
                    raise ValueError(f"权限ID {permission_id} 不存在")
                if permission in role.permissions:
                    role.permissions.remove(permission)
                else:
                    raise ValueError(f"该角色没有权限ID {permission_id}")

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新角色权限失败: {str(e)}")
            raise

    @staticmethod
    def set_role_permissions(role_id, permission_ids):
        """
        设置角色权限（替换现有权限）

        Args:
            role_id (int): 角色ID
            permission_ids (list): 新的权限ID列表
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                raise ValueError("角色不存在")

            # 验证所有权限是否存在
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if not permission:
                    raise ValueError(f"权限ID {permission_id} 不存在")

            # 清空现有权限
            role.permissions.clear()

            # 添加新权限
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                role.permissions.append(permission)

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"设置角色权限失败: {str(e)}")
            raise

    @staticmethod
    def get_permissions():
        """
        获取所有权限

        Returns:
            list: 权限列表
        """
        try:
            permissions = Permission.query.all()

            # 转换为字典列表
            permission_dicts = [{
                'id': perm.id,
                'code': perm.code,
                'resource': perm.resource,
                'action': perm.action,
                'scope': perm.scope,
                'description': perm.description
            } for perm in permissions]

            return permission_dicts
        except Exception as e:
            logger.error(f"获取所有权限失败: {str(e)}")
            raise

    @staticmethod
    def get_role_permissions(role_id):
        """
        获取角色权限

        Args:
            role_id (int): 角色ID

        Returns:
            list: 权限列表
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                raise ValueError("角色不存在")

            # 获取角色权限
            permissions = role.permissions

            # 转换为字典列表
            permission_dicts = [{
                'id': perm.id,
                'code': perm.code,
                'resource': perm.resource,
                'action': perm.action,
                'scope': perm.scope,
                'description': perm.description
            } for perm in permissions]

            return permission_dicts
        except Exception as e:
            logger.error(f"获取角色权限失败: {str(e)}")
            raise

    @staticmethod
    def update_user_permissions(staff_id, permission_ids):
        """
        更新用户权限

        Args:
            staff_id (int): 人员ID
            permission_ids (list): 新的权限ID列表

        Returns:
            bool: 是否成功
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 验证权限是否存在
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if not permission:
                    raise ValueError(f"权限ID {permission_id} 不存在")

            # 清空用户现有权限
            staff.permissions.clear()

            # 添加新的权限
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                staff.permissions.append(permission)

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新用户权限失败: {str(e)}")
            raise

    @staticmethod
    def add_user_permissions(staff_id, permission_ids):
        """
        分配权限给用户（追加模式）

        Args:
            staff_id (int): 人员ID
            permission_ids (list): 权限ID列表

        Returns:
            bool: 是否成功
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 验证权限是否存在
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if not permission:
                    raise ValueError(f"权限ID {permission_id} 不存在")

            # 直接分配权限给用户
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if permission not in staff.permissions:
                    staff.permissions.append(permission)

            # 保存更改
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"分配用户权限失败: {str(e)}")
            raise

    @staticmethod
    def update_staff_status(staff_id: int, status: int):
        """
        更新人员状态

        Args:
            staff_id (int): 人员ID
            status (int): 状态值 (0-删除、1-正常、2-禁用)

        Returns:
            dict: 更新后的人员信息
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 验证状态值是否有效
            if status not in [0, 1, 2]:
                raise ValueError("无效的状态值，必须是0、1或2")

            staff.status = status
            db.session.commit()

            return staff.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新人员状态失败: {str(e)}")
            raise

    @staticmethod
    def delete_role(role_id):
        """
        删除角色（逻辑删除，将is_active设置为False）

        Args:
            role_id (int): 角色ID

        Returns:
            bool: 是否成功
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                raise ValueError("角色不存在")

            # 逻辑删除角色
            role.is_active = False
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除角色失败: {str(e)}")
            raise

    @staticmethod
    def update_user_password(staff_id: int, new_password: str):
        """
        修改用户密码

        Args:
            staff_id (int): 人员ID
            new_password (str): 新密码

        Returns:
            dict: 更新后的用户信息
        """
        try:
            staff = User.query.get(staff_id)
            if not staff or staff.deleted_at:
                raise ValueError("人员不存在")

            # 设置新密码
            staff.set_password(new_password)
            db.session.commit()

            return staff.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"修改用户密码失败: {str(e)}")
            raise

    @staticmethod
    def get_all_roles_with_permissions():
        """
        获取所有角色及其权限

        Returns:
            list: 包含所有角色及其权限的列表
        """
        try:
            # 获取所有角色
            roles = Role.query.filter_by(is_active=True).all()

            # 构建角色及其权限的列表
            roles_with_permissions = []
            for role in roles:
                # 获取角色权限
                permissions = role.permissions
                permission_dicts = [{
                    'id': perm.id,
                    'code': perm.code,
                    'resource': perm.resource,
                    'action': perm.action,
                    'scope': perm.scope,
                    'description': perm.description
                } for perm in permissions]

                # 添加角色信息及其权限
                roles_with_permissions.append({
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'parent_id': role.parent_id,
                    'created_at': datetime_to_string(role.created_at, '%Y-%m-%d %H:%M:%S'),
                    'permissions': permission_dicts
                })

            return roles_with_permissions
        except Exception as e:
            logger.error(f"获取所有角色及其权限失败: {str(e)}")
            raise