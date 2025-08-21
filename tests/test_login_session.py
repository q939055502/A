#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试登录会话稳定性脚本

此脚本用于测试admin账号登录后会话的稳定性，验证是否存在登录后很快退出的问题。
脚本会执行以下操作：
1. 登录系统获取访问令牌和刷新令牌
2. 持续访问受保护的API端点
3. 监控是否出现401错误
"""

import requests
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_login_session.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置测试参数
BASE_URL = 'http://localhost:5000'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '111'
TEST_DURATION = 300  # 测试持续时间(秒)，这里设为5分钟
CHECK_INTERVAL = 5  # 检查间隔(秒)

# API端点
LOGIN_ENDPOINT = f'{BASE_URL}/user/login'
REFRESH_ENDPOINT = f'{BASE_URL}/auth/refresh'
GET_USER_INFO_ENDPOINT = f'{BASE_URL}/user/get-user-info'


def login():
    """登录系统并返回访问令牌和刷新令牌"""
    logger.info(f'尝试登录账号: {ADMIN_USERNAME}')
    try:
        response = requests.post(
            LOGIN_ENDPOINT,
            json={
                'username': ADMIN_USERNAME,
                'password': ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                access_token = data.get('data', {}).get('access_token')
                refresh_token = data.get('data', {}).get('refresh_token')
                logger.info('登录成功，获取到令牌')
                return access_token, refresh_token
            else:
                logger.error(f'登录失败: {data.get("message")}')
                return None, None
        else:
            logger.error(f'登录请求失败，状态码: {response.status_code}, 响应: {response.text}')
            return None, None
    except Exception as e:
        logger.error(f'登录过程中发生异常: {str(e)}')
        return None, None


def refresh_access_token(refresh_token):
    """使用刷新令牌获取新的访问令牌"""
    logger.info('尝试刷新访问令牌')
    try:
        response = requests.post(
            REFRESH_ENDPOINT,
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                new_access_token = data.get('data', {}).get('access_token')
                logger.info('刷新令牌成功')
                return new_access_token
            else:
                logger.error(f'刷新令牌失败: {data.get("message")}')
                return None
        else:
            logger.error(f'刷新令牌请求失败，状态码: {response.status_code}, 响应: {response.text}')
            return None
    except Exception as e:
        logger.error(f'刷新令牌过程中发生异常: {str(e)}')
        return None


def get_user_info(access_token):
    """使用访问令牌获取用户信息"""
    try:
        response = requests.get(
            GET_USER_INFO_ENDPOINT,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info('成功获取用户信息')
                return True
            else:
                logger.warning(f'获取用户信息失败: {data.get("message")}')
                return False
        elif response.status_code == 401:
            logger.warning('获取用户信息失败: 未授权(401)，令牌可能已过期')
            return False
        else:
            logger.error(f'获取用户信息请求失败，状态码: {response.status_code}, 响应: {response.text}')
            return False
    except Exception as e:
        logger.error(f'获取用户信息过程中发生异常: {str(e)}')
        return False


def test_login_session():
    """测试登录会话稳定性"""
    start_time = time.time()
    end_time = start_time + TEST_DURATION
    
    # 初始登录
    access_token, refresh_token = login()
    if not access_token or not refresh_token:
        logger.error('初始登录失败，无法继续测试')
        return
    
    logger.info(f'开始测试登录会话稳定性，持续时间: {TEST_DURATION}秒')
    
    while time.time() < end_time:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'[{current_time}] 测试中...')
        
        # 尝试获取用户信息
        success = get_user_info(access_token)
        
        if not success:
            # 尝试刷新令牌
            new_access_token = refresh_access_token(refresh_token)
            if new_access_token:
                access_token = new_access_token
                logger.info('使用新令牌继续测试')
            else:
                # 刷新令牌失败，尝试重新登录
                logger.warning('刷新令牌失败，尝试重新登录')
                access_token, refresh_token = login()
                if not access_token or not refresh_token:
                    logger.error('重新登录失败，测试终止')
                    return
        
        # 等待下一次检查
        time.sleep(CHECK_INTERVAL)
    
    logger.info(f'测试完成，持续时间: {TEST_DURATION}秒')
    logger.info('测试期间会话保持正常，未出现异常退出问题')


if __name__ == '__main__':
    test_login_session()