import click
from flask import current_app
from app.db import db
from app.models.user.role import Role
from app.models.user.permission import Permission
from app.models.user.user import User
from datetime import datetime, timezone

@click.command('init-permissions')
def init_permissions():
    """初始化系统角色和权限"""
    with current_app.app_context():
        click.echo('开始初始化角色和权限...')

        # 先清除现有数据
        click.echo('清除现有角色和权限数据...')
        # 先删除关联表数据
        db.session.execute('DELETE FROM role_permissions')
        db.session.execute('DELETE FROM user_roles')
        db.session.execute('DELETE FROM user_permissions')
        # 再删除角色和权限数据
        Role.query.delete()
        Permission.query.delete()
        db.session.commit()

        # 创建权限
        click.echo('创建权限...')

        # 1.1 用户管理权限
        user_permissions = [
            {'code': 'user:view:own', 'resource': 'user', 'action': 'view', 'scope': 'own', 'description': '查看自己的用户信息'}, 
            {'code': 'user:view:all', 'resource': 'user', 'action': 'view', 'scope': 'all', 'description': '查看所有用户信息'}, 
            {'code': 'user:create', 'resource': 'user', 'action': 'create', 'scope': 'all', 'description': '创建新用户'}, 
            {'code': 'user:edit:own', 'resource': 'user', 'action': 'edit', 'scope': 'own', 'description': '编辑自己的用户信息'}, 
            {'code': 'user:edit:all', 'resource': 'user', 'action': 'edit', 'scope': 'all', 'description': '编辑所有用户信息'}, 
            {'code': 'user:delete', 'resource': 'user', 'action': 'delete', 'scope': 'all', 'description': '删除用户'}, 
            {'code': 'user:export', 'resource': 'user', 'action': 'export', 'scope': 'all', 'description': '导出用户数据'}, 
            {'code': 'user:role:manage', 'resource': 'user', 'action': 'role:manage', 'scope': 'all', 'description': '管理用户角色'}, 
            {'code': 'user:permission:manage', 'resource': 'user', 'action': 'permission:manage', 'scope': 'all', 'description': '管理用户权限'} 
        ]

        # 1.2 检测报告管理权限
        report_permissions = [
            {'code': 'inspection_report:view:own', 'resource': 'inspection_report', 'action': 'view', 'scope': 'own', 'description': '查看自己的检测报告'}, 
            {'code': 'inspection_report:view:all', 'resource': 'inspection_report', 'action': 'view', 'scope': 'all', 'description': '查看所有检测报告'}, 
            {'code': 'inspection_report:create', 'resource': 'inspection_report', 'action': 'create', 'scope': 'all', 'description': '创建检测报告'}, 
            {'code': 'inspection_report:edit:own', 'resource': 'inspection_report', 'action': 'edit', 'scope': 'own', 'description': '编辑自己的检测报告'}, 
            {'code': 'inspection_report:edit:all', 'resource': 'inspection_report', 'action': 'edit', 'scope': 'all', 'description': '编辑所有检测报告'}, 
            {'code': 'inspection_report:delete:own', 'resource': 'inspection_report', 'action': 'delete', 'scope': 'own', 'description': '删除自己的检测报告'}, 
            {'code': 'inspection_report:delete:all', 'resource': 'inspection_report', 'action': 'delete', 'scope': 'all', 'description': '删除所有检测报告'}, 
            {'code': 'inspection_report:approve:all', 'resource': 'inspection_report', 'action': 'approve', 'scope': 'all', 'description': '审批检测报告'}, 
            {'code': 'inspection_report:export', 'resource': 'inspection_report', 'action': 'export', 'scope': 'all', 'description': '导出检测报告'}, 
            {'code': 'inspection_report:print', 'resource': 'inspection_report', 'action': 'print', 'scope': 'all', 'description': '打印检测报告'} 
        ]

        # 1.3 公告管理权限
        announcement_permissions = [
            {'code': 'announcement:view:all', 'resource': 'announcement', 'action': 'view', 'scope': 'all', 'description': '查看所有公告'}, 
            {'code': 'announcement:create', 'resource': 'announcement', 'action': 'create', 'scope': 'all', 'description': '创建公告'}, 
            {'code': 'announcement:edit:all', 'resource': 'announcement', 'action': 'edit', 'scope': 'all', 'description': '编辑所有公告'}, 
            {'code': 'announcement:delete:all', 'resource': 'announcement', 'action': 'delete', 'scope': 'all', 'description': '删除所有公告'}, 
            {'code': 'announcement:pin:manage', 'resource': 'announcement', 'action': 'pin:manage', 'scope': 'all', 'description': '管理公告置顶状态'}, 
            {'code': 'announcement:active:manage', 'resource': 'announcement', 'action': 'active:manage', 'scope': 'all', 'description': '管理公告激活状态'} 
        ]

        # 1.4 系统管理权限
        system_permissions = [
            {'code': 'system:role:manage', 'resource': 'system', 'action': 'role:manage', 'scope': 'all', 'description': '管理角色'}, 
            {'code': 'system:permission:manage', 'resource': 'system', 'action': 'permission:manage', 'scope': 'all', 'description': '管理权限'}, 
            {'code': 'system:config:edit', 'resource': 'system', 'action': 'config:edit', 'scope': 'all', 'description': '编辑系统参数'}, 
            {'code': 'system:log:view', 'resource': 'system', 'action': 'log:view', 'scope': 'all', 'description': '查看系统日志'} 
        ]

        # 合并所有权限
        permissions = user_permissions + report_permissions + announcement_permissions + system_permissions

        # 创建权限记录
        permission_objects = {}
        for perm_data in permissions:
            permission = Permission.query.filter_by(code=perm_data['code']).first()
            if not permission:
                permission = Permission(
                    code=perm_data['code'],
                    resource=perm_data['resource'],
                    action=perm_data['action'],
                    scope=perm_data.get('scope', 'all'),
                    description=perm_data['description'],
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(permission)
            permission_objects[perm_data['code']] = permission

        # 提交权限到数据库
        db.session.commit()

        # 创建角色
        click.echo('创建角色...')

        roles = [
            {'name': 'admin', 'description': '系统管理员角色，拥有最高权限', 'parent_id': None}, 
            {'name': 'auditor', 'description': '审核者角色，负责审批检测报告', 'parent_id': None}, 
            {'name': 'editor', 'description': '编辑者角色，负责创建和编辑内容', 'parent_id': None}, 
            {'name': 'user', 'description': '普通用户角色，拥有个人信息管理权限', 'parent_id': None}, 
            {'name': 'viewer', 'description': '访客角色，拥有只读权限', 'parent_id': None} 
        ]

        # 创建角色记录
        role_objects = {}
        for role_data in roles:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(
                    name=role_data['name'],
                    description=role_data['description'],
                    created_at=datetime.now(timezone.utc)
                )
                db.session.add(role)
            role_objects[role_data['name']] = role

        # 提交角色到数据库
        db.session.commit()

        # 为角色分配权限
        click.echo('为角色分配权限...')

        # 管理员权限
        admin_permission_codes = [
            'user:view:own', 'user:view:all', 'user:create', 'user:edit:own', 'user:edit:all',
            'user:delete', 'user:export', 'user:role:manage', 'user:permission:manage',
            'inspection_report:view:own', 'inspection_report:view:all', 'inspection_report:create',
            'inspection_report:edit:own', 'inspection_report:edit:all', 'inspection_report:delete:own',
            'inspection_report:delete:all', 'inspection_report:approve:all', 'inspection_report:export',
            'inspection_report:print', 'announcement:view:all', 'announcement:create', 'announcement:edit:all',
            'announcement:delete:all', 'announcement:pin:manage', 'announcement:active:manage',
            'system:role:manage', 'system:permission:manage', 'system:config:edit', 'system:log:view'
        ]
        for code in admin_permission_codes:
            perm = permission_objects.get(code)
            if perm and perm not in role_objects['admin'].permissions:
                role_objects['admin'].permissions.append(perm)

        # 审核者权限
        auditor_permission_codes = [
            'user:view:all', 'inspection_report:view:all', 'inspection_report:approve:all'
        ]
        for code in auditor_permission_codes:
            perm = permission_objects.get(code)
            if perm and perm not in role_objects['auditor'].permissions:
                role_objects['auditor'].permissions.append(perm)

        # 编辑者权限
        editor_permission_codes = [
            'inspection_report:create', 'inspection_report:view:all', 'inspection_report:edit:all',
            'inspection_report:delete:all', 'announcement:create', 'announcement:view:all',
            'announcement:edit:all', 'announcement:delete:all', 'user:view:all', 'user:edit:all'
        ]
        for code in editor_permission_codes:
            perm = permission_objects.get(code)
            if perm and perm not in role_objects['editor'].permissions:
                role_objects['editor'].permissions.append(perm)

        # 普通用户权限
        user_permission_codes = [
            'user:view:own', 'user:edit:own', 'inspection_report:view:all',
            'inspection_report:create', 'inspection_report:edit:own', 'inspection_report:delete:own'
        ]
        for code in user_permission_codes:
            perm = permission_objects.get(code)
            if perm and perm not in role_objects['user'].permissions:
                role_objects['user'].permissions.append(perm)

        # 访客权限
        viewer_permission_codes = [
            'user:view:own', 'inspection_report:view:all', 'announcement:view:all'
        ]
        for code in viewer_permission_codes:
            perm = permission_objects.get(code)
            if perm and perm not in role_objects['viewer'].permissions:
                role_objects['viewer'].permissions.append(perm)

        # 提交角色权限关联
        db.session.commit()

        # 创建或更新默认管理员用户
        click.echo('创建或更新默认管理员用户...')
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            click.echo('管理员用户已存在，更新角色...')
            # 确保用户状态为启用
            admin_user.status = 1
            # 更新角色（先清空现有角色）
            admin_user.roles = [role_objects['admin']]
            db.session.commit()
        else:
            click.echo('创建新的管理员用户...')
            admin_user = User(
                username='admin',
                email='admin@example.com',
                phone_number='13800138000',
                nickname='管理员',
                status=1
            )
            admin_user.set_password('111')  # 设置密码
            admin_user.roles.append(role_objects['admin'])
            db.session.add(admin_user)
            db.session.commit()

        click.echo('角色和权限初始化完成！')
        click.echo(f'创建了 {len(permissions)} 个权限')
        click.echo(f'创建了 {5} 个角色')
        click.echo('创建了默认管理员用户: admin@example.com')

def register_command(app):
    """将命令注册到应用对象"""
    app.cli.add_command(init_permissions)