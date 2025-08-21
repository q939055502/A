#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""数据迁移脚本

此脚本用于项目迁移时的数据迁移操作，包括：
1. 备份现有数据库
2. 应用数据库迁移
3. 初始化角色和权限
4. 创建测试数据
"""

import os
import sys
import shutil
import subprocess
import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.db import db

# 创建Flask应用实例
app = create_app()

# 确保中文显示正常
os.environ['PYTHONIOENCODING'] = 'utf-8'

class DataMigrator:
    def __init__(self, app):
        self.app = app
        self.db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        self.backup_dir = os.path.join(app.root_path, 'backups')
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    def backup_database(self):
        """备份数据库"""
        print("开始备份数据库...")

        # 创建备份目录
        os.makedirs(self.backup_dir, exist_ok=True)

        if self.db_uri.startswith('mysql'):
            # MySQL数据库备份
            try:
                # 解析数据库连接信息
                from urllib.parse import urlparse
                parsed_uri = urlparse(self.db_uri)
                db_name = parsed_uri.path.lstrip('/').split('?')[0]
                user = parsed_uri.username
                password = parsed_uri.password
                host = parsed_uri.hostname
                port = parsed_uri.port or 3306

                backup_file = os.path.join(self.backup_dir, f'{db_name}_backup_{self.timestamp}.sql')

                # 使用mysqldump命令备份
                cmd = [
                    'mysqldump',
                    f'--user={user}',
                    f'--password={password}',
                    f'--host={host}',
                    f'--port={port}',
                    db_name,
                    f'--result-file={backup_file}'
                ]

                print(f"执行命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"数据库备份成功: {backup_file}")
                    return backup_file
                else:
                    print(f"数据库备份失败: {result.stderr}")
                    return None
            except Exception as e:
                print(f"备份数据库时出错: {str(e)}")
                return None
        elif self.db_uri.startswith('sqlite'):
            # SQLite数据库备份
            try:
                db_path = self.db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    backup_file = os.path.join(self.backup_dir, f'sqlite_backup_{self.timestamp}.db')
                    shutil.copy2(db_path, backup_file)
                    print(f"SQLite数据库备份成功: {backup_file}")
                    return backup_file
                else:
                    print(f"SQLite数据库文件不存在: {db_path}")
                    return None
            except Exception as e:
                print(f"备份SQLite数据库时出错: {str(e)}")
                return None
        else:
            print(f"不支持的数据库类型: {self.db_uri}")
            return None

    def apply_migrations(self):
        """应用数据库迁移"""
        print("开始应用数据库迁移...")
        try:
            # 使用Flask-Migrate应用迁移
            cmd = [
                sys.executable,
                '-m', 'flask',
                'db', 'upgrade'
            ]

            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("数据库迁移应用成功")
                return True
            else:
                print(f"数据库迁移应用失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"应用数据库迁移时出错: {str(e)}")
            return False

    def initialize_roles_permissions(self):
        """初始化角色和权限"""
        print("开始初始化角色和权限...")
        try:
            # 运行initialize_roles_permissions.py脚本
            script_path = os.path.join(os.path.dirname(__file__), 'initialize_roles_permissions.py')
            cmd = [sys.executable, script_path]

            print(f"执行命令: {' '.join(cmd)}")
            # 指定encoding='utf-8'以避免Unicode解码错误
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            # 打印脚本的标准输出和错误输出
            print(f"initialize_roles_permissions.py 输出:\n{result.stdout}")
            if result.stderr:
                print(f"initialize_roles_permissions.py 错误输出:\n{result.stderr}")

            if result.returncode == 0:
                print("角色和权限初始化成功")
                return True
            else:
                print(f"角色和权限初始化失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"初始化角色和权限时出错: {str(e)}")
            return False

    # 注意：create_test_data方法已被移除，测试数据将通过initialize_roles_permissions.py创建

    def migrate(self):
        """执行完整的数据迁移流程"""
        with self.app.app_context():
            # 1. 备份数据库
            backup_file = self.backup_database()
            if not backup_file:
                print("数据库备份失败，是否继续迁移? (y/n)")
                choice = input().strip().lower()
                if choice != 'y':
                    print("迁移操作已取消")
                    return False

            # 2. 应用数据库迁移
            if not self.apply_migrations():
                print("数据库迁移失败，迁移操作已取消")
                return False

            # 3. 初始化角色和权限
            if not self.initialize_roles_permissions():
                print("角色和权限初始化失败，迁移操作已取消")
                return False

            print("\n数据迁移流程已完成！")
            print(f"1. 数据库已备份到: {backup_file}")
            print("2. 数据库结构已更新")
            print("3. 角色和权限已初始化（包含测试用户数据）")
            print("\n管理员账号: admin")
            print("管理员密码: abcd13579")
            print("测试用户账号: user1-user10")
            print("测试用户密码: 111")
            return True

if __name__ == '__main__':
    migrator = DataMigrator(app)
    success = migrator.migrate()
    sys.exit(0 if success else 1)