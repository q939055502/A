# -*- coding: utf-8 -*-
"""
测试并打印用户权限和角色信息
"""
import os
import sys
import requests
import json

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# 测试配置
BASE_URL = 'http://localhost:5000'
TEST_USERNAME = 'user5'
TEST_PASSWORD = '111'

def login():
    """登录用户并返回访问令牌"""
    login_url = f'{BASE_URL}/user/login'
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }

    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data.get('data', {}).get('token')
                print(f'登录成功！获取到令牌: {token[:20]}...')
                return token
            else:
                print(f'登录失败: {data.get("message")}')
                return None
        else:
            print(f'登录请求失败，状态码: {response.status_code}')
            print(f'响应内容: {response.text}')
            return None
    except Exception as e:
        print(f'登录过程中发生错误: {str(e)}')
        return None

def get_user_info(token):
    """使用访问令牌获取用户信息"""
    if not token:
        print('没有提供访问令牌')
        return None

    user_info_url = f'{BASE_URL}/auth/get-user-info'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(user_info_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data = data.get('data', {})
                print('成功获取用户信息')
                return user_data
            else:
                print(f'获取用户信息失败: {data.get("message")}')
                return None
        else:
            print(f'获取用户信息请求失败，状态码: {response.status_code}')
            print(f'响应内容: {response.text}')
            return None
    except Exception as e:
        print(f'获取用户信息过程中发生错误: {str(e)}')
        return None

def print_user_permissions(user_data):
    """打印用户的角色和权限信息"""
    if not user_data:
        print('没有提供用户数据')
        return

    # 打印用户基本信息
    print(f'\n用户基本信息:')
    print(f'用户名: {user_data.get("username")}')
    print(f'用户ID: {user_data.get("id")}')
    print(f'邮箱: {user_data.get("email")}')

    # 打印用户角色
    roles = user_data.get('roles', [])
    print(f'\n用户角色:')
    if roles:
        for role in roles:
            print(f'- {role}')
    else:
        print('- 无角色')

    # 打印用户权限
    permissions = user_data.get('permissions', [])
    print(f'\n用户权限:')
    if permissions:
        for perm in permissions:
            print(f'- 代码: {perm.get("code")}')
            print(f'  资源: {perm.get("resource")}')
            print(f'  操作: {perm.get("action")}')
            print(f'  范围: {perm.get("scope")}')
    else:
        print('- 无权限')

if __name__ == '__main__':
    print('开始测试打印用户权限和角色信息...')
    # 登录获取令牌
    token = login()
    if token:
        # 使用令牌获取用户信息
        user_data = get_user_info(token)
        if user_data:
            # 打印用户权限和角色
            print_user_permissions(user_data)
    print('测试完成')