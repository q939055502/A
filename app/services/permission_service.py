from app.models.user.user import User
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.db import db

class PermissionService:
    """权限服务类，集中管理用户、角色、权限的关系判断"""

    @staticmethod
    def has_user_role(user, role_name):
        """检查用户是否拥有指定角色"""
        user_roles = [role.name for role in user.roles]
        has_role = any(role.name == role_name for role in user.roles)

        return has_role

    @staticmethod
    def get_roles_and_permissions(user):
        """获取用户的所有角色和权限"""
        # 确保加载用户角色
        db.session.refresh(user)
        # 获取所有角色名称
        roles = [role.name for role in user.roles]

        # 获取用户权限
        permissions = PermissionService.get_user_permissions(user)
        permission_dicts = [{
            'code': perm.code,
            'resource': perm.resource,
            'action': perm.action,
            'scope': perm.scope
        } for perm in permissions]

        return {
            'roles': roles,
            'permissions': permission_dicts
        }

    @staticmethod
    def has_user_permission(user, resource, action, scope='all', resource_id=None):
        """检查用户是否拥有指定资源的操作权限

        Args:
            user: 用户对象
            resource: 资源名称
            action: 操作类型
            scope: 权限范围，默认为'all'
            resource_id: 资源ID，当scope为'own'时需要传入

        Returns:
            bool: 是否拥有权限
        """
        # 优先检查用户直接拥有的'all'权限
        for perm in user.permissions:
            if perm.scope == 'all' and PermissionService._check_permission(perm, resource, action, 'all', user, None):
                return True

        # 然后检查用户角色拥有的'all'权限
        for role in user.roles:
            if PermissionService.has_role_permission(role, resource, action, 'all', user, None):
                return True

        # 如果请求的不是'all'权限，再检查指定scope的权限
        if scope != 'all':
            # 检查用户直接拥有的指定scope权限
            for perm in user.permissions:
                if PermissionService._check_permission(perm, resource, action, scope, user, resource_id):
                    return True

            # 检查用户角色拥有的指定scope权限
            for role in user.roles:
                if PermissionService.has_role_permission(role, resource, action, scope, user, resource_id):
                    return True

        return False

    @staticmethod
    def has_role_permission(role, resource, action, scope='all', user=None, resource_id=None, checked_roles=None):
        """检查角色是否拥有指定资源的操作权限"""
        # 初始化已检查角色集合，避免循环引用
        if checked_roles is None:
            checked_roles = set()
        # 若当前角色已检查过，直接返回False（避免循环）
        if role.id in checked_roles:
    
            return False
        checked_roles.add(role.id)

        # 如果请求的不是'all'权限，先检查是否有对应的'all'权限
        if scope != 'all':
            for perm in role.permissions:
                if perm.scope == 'all' and PermissionService._check_permission(perm, resource, action, 'all', user, None):
                    return True

            # 递归检查父角色是否有'all'权限
            if role.parent:
                if PermissionService.has_role_permission(role.parent, resource, action, 'all', user, None, checked_roles.copy()):
                    return True

        # 检查当前角色指定scope的权限
        for perm in role.permissions:
            if PermissionService._check_permission(perm, resource, action, scope, user, resource_id):
                return True

        # 递归检查父角色指定scope的权限
        if role.parent:
            return PermissionService.has_role_permission(role.parent, resource, action, scope, user, resource_id, checked_roles)

        return False

    @staticmethod
    def _check_permission(permission, resource, action, scope='all', user=None, resource_id=None):
        """检查单个权限是否匹配资源、操作和范围

        当scope为'own'时，还需验证用户是否为资源的所有者
        """
        is_active = permission.is_active
        resource_match = permission.resource == resource
        action_match = permission.action == action
        scope_match = permission.scope == 'all' or permission.scope == scope

        # 基础权限检查不通过，直接返回False
        if not (is_active and resource_match and action_match and scope_match):
            return False

        # 需求1: 前三个参数为true(即is_active, resource_match, action_match都为True)
        # 如果scope_match也为True且未传入resource_id(使用默认值)且scope不是'own'，则返回True
        if is_active and resource_match and action_match and scope_match and resource_id is None and scope != 'own':
            return True

        # 需求2: 前两个参数为true(即is_active, resource_match都为True)
        # 如果action_match也为True且未传入scope和resource_id(都使用默认值)，则返回True
        if is_active and resource_match and action_match and scope == 'all' and resource_id is None:
            return True

        # 如果scope为'own'，需要额外检查用户是否为资源所有者
        if scope == 'own' and resource_id != None:
            # 确保提供了resource_id和user
            if not resource_id or not user:
                return False

            try:
                # 根据资源类型和ID查询资源并检查所有权
                resource_type_config = {
                    'inspection_report': {
                        'model': 'app.models.report.inspection_report.InspectionReport',
                        'query_field': 'report_code',
                        'owner_field': 'registrant_id'
                    },
                    'user': {
                        'model': 'app.models.user.user.User',
                        'query_field': 'id',
                        'owner_field': 'id'
                    }
                    # 可根据需要添加其他资源类型的配置
                }

                if resource in resource_type_config:
                    config = resource_type_config[resource]
                    # 动态导入模型
                    from importlib import import_module
                    module_path, class_name = config['model'].rsplit('.', 1)
                    module = import_module(module_path)
                    model_class = getattr(module, class_name)
                    
                    # 构建查询 kwargs
                    query_kwargs = {config['query_field']: resource_id}
                    resource_instance = model_class.query.filter_by(**query_kwargs).first()
                    
                    if not resource_instance:
                        return False
                    
                    # 比较用户ID与资源的所有者字段是否一致
                    owner_id = getattr(resource_instance, config['owner_field'])
                    return str(user.id) == str(owner_id)
                else:
                    # 对于未配置的资源类型，返回False
                    return False
            except Exception as e:
                # 发生异常时，返回False
                return False

        return True

    @staticmethod
    def get_user_permissions(user):
        """获取用户的所有有效权限"""
        # print(f"PermissionService: 获取用户 {user.id} 的所有有效权限...")
        permissions = []
        permission_codes = set()

        # 添加用户直接拥有的有效权限
        # print(f"PermissionService: 添加用户 {user.id} 直接拥有的有效权限...")
        for perm in user.permissions:
            if perm.is_active and perm.code not in permission_codes:
                # print(f"PermissionService: 添加用户直接权限: {perm.code} ({perm.resource}:{perm.action}:{perm.scope})")
                permissions.append(perm)
                permission_codes.add(perm.code)
            elif not perm.is_active:
                # print(f"PermissionService: 跳过非激活权限: {perm.code}")
                pass
            else:
                # print(f"PermissionService: 跳过重复权限: {perm.code}")
                pass

        # 添加用户角色拥有的有效权限
        # print(f"PermissionService: 添加用户 {user.id} 角色拥有的有效权限...")
        checked_roles = set()
        for role in user.roles:
            # print(f"PermissionService: 处理角色 '{role.name}'...")
            PermissionService._add_role_permissions(role, permissions, permission_codes, checked_roles)

        # print(f"PermissionService: 用户 {user.id} 共拥有 {len(permissions)} 个有效权限")
        return permissions

    @staticmethod
    def _add_role_permissions(role, permissions, permission_codes, checked_roles):
        """递归添加角色及其父角色的有效权限"""
        # 避免循环引用
        if role.id in checked_roles:
            # print(f"PermissionService: 角色 '{role.name}' (ID={role.id}) 已处理过，跳过")
            return
        checked_roles.add(role.id)

        # print(f"PermissionService: 处理角色 '{role.name}' (ID={role.id}) 的权限...")

        # 添加当前角色的有效权限
        for perm in role.permissions:
            if perm.is_active and perm.code not in permission_codes:
                # print(f"PermissionService: 添加角色权限: {perm.code} ({perm.resource}:{perm.action}:{perm.scope}) 来自角色 '{role.name}'")
                permissions.append(perm)
                permission_codes.add(perm.code)
            elif not perm.is_active:
                # print(f"PermissionService: 跳过角色 '{role.name}' 的非激活权限: {perm.code}")
                pass
            else:
                # print(f"PermissionService: 跳过角色 '{role.name}' 的重复权限: {perm.code}")
                pass

        # 递归添加父角色的有效权限
        if role.parent:
            # print(f"PermissionService: 递归处理角色 '{role.name}' 的父角色 '{role.parent.name}'...")
            PermissionService._add_role_permissions(role.parent, permissions, permission_codes, checked_roles)
        else:
            # print(f"PermissionService: 角色 '{role.name}' 没有父角色")
            pass