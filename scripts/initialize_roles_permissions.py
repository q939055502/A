#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""角色与权限初始化脚本

此脚本用于初始化系统中的角色和权限数据，根据docs/角色与权限.md文档定义
"""

import os
import sys
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.db import db
from sqlalchemy import text
from app.models.user.permission import Permission
from app.models.user.role import Role
from app.models.user.user import User
from datetime import datetime, timezone

# 创建Flask应用实例
app = create_app()

# 确保在应用上下文中运行
with app.app_context():
    try:
        print("开始初始化角色和权限...")

        # 先清除现有数据
        print("清除现有角色和权限数据...")
        # 先删除关联表数据
        db.session.execute(text('DELETE FROM role_permissions'))
        db.session.execute(text('DELETE FROM user_roles'))
        db.session.execute(text('DELETE FROM user_permissions'))
        # 再删除角色和权限数据
        Role.query.delete()
        Permission.query.delete()
        db.session.commit()

        # 创建权限
        print("创建权限...")

        # 1.1 用户管理权限
        user_permissions = [
            Permission(code='user:view:own', resource='user', action='view', scope='own', description='查看自己的用户信息'),
            Permission(code='user:view:all', resource='user', action='view', scope='all', description='查看所有用户信息'),
            Permission(code='user:create', resource='user', action='create', scope='all', description='创建新用户'),
            Permission(code='user:edit:own', resource='user', action='edit', scope='own', description='编辑自己的用户信息'),
            Permission(code='user:edit:all', resource='user', action='edit', scope='all', description='编辑所有用户信息'),
            Permission(code='user:delete', resource='user', action='delete', scope='all', description='删除用户'),
            Permission(code='user:export', resource='user', action='export', scope='all', description='导出用户数据'),
            Permission(code='user:role:manage', resource='user', action='role:manage', scope='all', description='管理用户角色'),
            Permission(code='user:permission:manage', resource='user', action='permission:manage', scope='all', description='管理用户权限')
        ]

        # 1.2 检测报告管理权限
        report_permissions = [
            Permission(code='inspection_report:view:own', resource='inspection_report', action='view', scope='own', description='查看自己的检测报告'),
            Permission(code='inspection_report:view:all', resource='inspection_report', action='view', scope='all', description='查看所有检测报告'),
            Permission(code='inspection_report:create', resource='inspection_report', action='create', scope='all', description='创建检测报告'),
            Permission(code='inspection_report:edit:own', resource='inspection_report', action='edit', scope='own', description='编辑自己的检测报告'),
            Permission(code='inspection_report:edit:all', resource='inspection_report', action='edit', scope='all', description='编辑所有检测报告'),
            Permission(code='inspection_report:delete:own', resource='inspection_report', action='delete', scope='own', description='删除自己的检测报告'),
            Permission(code='inspection_report:delete:all', resource='inspection_report', action='delete', scope='all', description='删除所有检测报告'),
            Permission(code='inspection_report:approve:all', resource='inspection_report', action='approve', scope='all', description='审批检测报告'),
            Permission(code='inspection_report:export', resource='inspection_report', action='export', scope='all', description='导出检测报告'),
            Permission(code='inspection_report:print', resource='inspection_report', action='print', scope='all', description='打印检测报告')
        ]

        # 1.3 公告管理权限
        announcement_permissions = [
            Permission(code='announcement:view:all', resource='announcement', action='view', scope='all', description='查看所有公告'),
            Permission(code='announcement:create', resource='announcement', action='create', scope='all', description='创建公告'),
            Permission(code='announcement:edit:all', resource='announcement', action='edit', scope='all', description='编辑所有公告'),
            Permission(code='announcement:delete:all', resource='announcement', action='delete', scope='all', description='删除所有公告'),
            Permission(code='announcement:pin:manage', resource='announcement', action='pin:manage', scope='all', description='管理公告置顶状态'),
            Permission(code='announcement:active:manage', resource='announcement', action='active:manage', scope='all', description='管理公告激活状态')
        ]

        # 1.4 系统管理权限
        system_permissions = [
            Permission(code='system:role:manage', resource='system', action='role:manage', scope='all', description='管理角色'),
            Permission(code='system:permission:manage', resource='system', action='permission:manage', scope='all', description='管理权限'),
            Permission(code='system:config:edit', resource='system', action='config:edit', scope='all', description='编辑系统参数'),
            Permission(code='system:log:view', resource='system', action='log:view', scope='all', description='查看系统日志')
        ]

        # 将所有权限添加到数据库
        all_permissions = user_permissions + report_permissions + announcement_permissions + system_permissions
        db.session.add_all(all_permissions)
        db.session.commit()

        # 创建角色
        print("创建角色...")

        # 4.1 管理员(admin)角色
        admin_role = Role(name='admin', description='系统管理员角色，拥有最高权限')

        # 4.2 审核者(auditor)角色
        auditor_role = Role(name='auditor', description='审核者角色，负责审批检测报告')

        # 4.3 编辑者(editor)角色
        editor_role = Role(name='editor', description='编辑者角色，负责创建和编辑内容')

        # 4.4 普通用户(user)角色
        user_role = Role(name='user', description='普通用户角色，拥有个人信息管理权限')

        # 4.5 访客(viewer)角色
        viewer_role = Role(name='viewer', description='访客角色，拥有只读权限')

        # 添加角色到数据库
        db.session.add_all([admin_role, auditor_role, editor_role, user_role, viewer_role])
        db.session.commit()

        # 为角色分配权限
        print("为角色分配权限...")

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
            perm = Permission.query.filter_by(code=code).first()
            if perm:
                admin_role.permissions.append(perm)

        # 审核者权限
        auditor_permission_codes = [
            'user:view:all', 'inspection_report:view:all', 'inspection_report:approve:all'
        ]
        for code in auditor_permission_codes:
            perm = Permission.query.filter_by(code=code).first()
            if perm:
                auditor_role.permissions.append(perm)

        # 编辑者权限
        editor_permission_codes = [
            'inspection_report:create', 'inspection_report:view:all', 'inspection_report:edit:all',
            'inspection_report:delete:all', 'announcement:create', 'announcement:view:all',
            'announcement:edit:all', 'announcement:delete:all', 'user:view:all', 'user:edit:all'
        ]
        for code in editor_permission_codes:
            perm = Permission.query.filter_by(code=code).first()
            if perm:
                editor_role.permissions.append(perm)

        # 普通用户权限
        user_permission_codes = [
            'user:view:own', 'user:edit:own', 'inspection_report:view:all',
            'inspection_report:create', 'inspection_report:edit:own', 'inspection_report:delete:own'
        ]
        for code in user_permission_codes:
            perm = Permission.query.filter_by(code=code).first()
            if perm:
                user_role.permissions.append(perm)

        # 访客权限
        viewer_permission_codes = [
            'user:view:own', 'inspection_report:view:all', 'announcement:view:all'
        ]
        for code in viewer_permission_codes:
            perm = Permission.query.filter_by(code=code).first()
            if perm:
                viewer_role.permissions.append(perm)

        # 提交角色权限关联
        db.session.commit()

        # 创建或更新默认管理员用户
        print("创建或更新默认管理员用户...")
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("管理员用户已存在，更新角色和密码...")
            # 更新密码
            admin_user.set_password('abcd13579')
            # 确保用户状态为启用
            admin_user.status = 1
            # 更新角色（先清空现有角色）
            admin_user.roles = [admin_role]
            db.session.commit()
        else:
            print("创建新的管理员用户...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                phone_number='13800138000',
                nickname='管理员',
                status=1
            )
            admin_user.set_password('abcd13579')  # 设置密码
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()

        # 创建10个测试用户并分配角色
        print("创建10个测试用户并分配角色...")
        roles = [admin_role, auditor_role, editor_role, user_role, viewer_role]
        user_count = 0
        
        # 先删除已存在的测试用户
        db.session.execute(text("DELETE FROM users WHERE username LIKE 'user%'"))
        db.session.commit()
        
        for i in range(1, 5):
            username = f'user{i}'
            email = f'{username}@example.com'
            
            # 为用户分配角色（每个角色2个用户）
            role_index = (i - 1) % len(roles)
            user_role_assigned = roles[role_index]
            
            new_user = User(
                username=username,
                email=email,
                phone_number=f'138001380{i:02d}',
                nickname=f'用户{i}',
                status=1
            )
            new_user.set_password('aaa111')
            new_user.roles.append(user_role_assigned)
            
            db.session.add(new_user)
            user_count += 1
            
            # 每5个用户提交一次
            if i % 5 == 0:
                db.session.commit()
                print(f"已创建 {i} 个测试用户...")
        
        db.session.commit()
        print(f"成功创建 {user_count} 个测试用户")

        print("角色和权限初始化完成！")
        print(f"创建了 {len(all_permissions)} 个权限")
        print(f"创建了 {5} 个角色")
        print(f"创建了 {1 + user_count} 个用户（1个管理员和{user_count}个测试用户）")

        
        print("创建测试公告...")
        try:
            from app.models.announcement import Announcement
            
            # 检查是否已存在测试公告
            existing_announcement = Announcement.query.filter_by(title='测试公告', is_deleted=False).first()
            if existing_announcement:
                print("测试公告已存在，跳过创建...")
            else:
                current_time = datetime.now(timezone.utc)
                new_announcement = Announcement(
                    title='测试公告',
                    content='这是一条系统初始化时创建的测试公告',
                    icon='https://example.com/announcement-icon.png',
                    is_active=True,
                    is_deleted=False,
                    priority=100,
                    start_date=current_time,
                    created_at=current_time,
                    updated_at=current_time,
                    created_by=admin_user.id
                )
                db.session.add(new_announcement)
                db.session.commit()
                print("测试公告创建成功！")
        except Exception as e:
            print(f"创建测试公告失败: {str(e)}")
            # 继续执行其他初始化操作，不中断整个流程


    except Exception as e:
        db.session.rollback()
        print(f"初始化失败: {str(e)}")
        sys.exit(1)
    finally:
        db.session.close()