import time
import requests
import json
import sys
import os

# 将项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# 测试配置
BASE_URL = 'http://localhost:5000'

# 测试用户配置
TEST_USER = {
    'username': 'test_user',
    'password': 'test_password',
    'email': 'test@example.com'
}

# 管理员账号配置
ADMIN_USER = {
    'username': 'admin',
    'password': '111'
}

# 发送邮箱验证码
def send_email_verification(email):
    url = f'{BASE_URL}/user/send-register-code'
    response = requests.post(url, json={'email': email})
    if response.status_code == 200:
        print('邮箱验证码发送成功')
        return True
    else:
        print(f'邮箱验证码发送失败: {response.status_code}, {response.text}')
        return False

# 注册测试用户
def register_test_user():
    # 先尝试登录，如果成功说明用户已存在
    access_token, _ = login()
    if access_token:
        print('测试用户已存在')
        return True

    # 发送邮箱验证码
    if not send_email_verification(TEST_USER['email']):
        return False

    # 等待验证码发送（实际应用中可能需要更长时间）
    time.sleep(2)

    # 直接使用已知的验证码进行测试
    # 注意：在实际测试环境中，应该从Redis或邮箱获取验证码
    TEST_USER['email_code'] = '123456'
    print(f'使用测试验证码: {TEST_USER["email_code"]}')

    # 注册用户
    url = f'{BASE_URL}/user/register'
    response = requests.post(url, json=TEST_USER)
    if response.status_code == 201:
        print('测试用户注册成功')
        return True
    else:
        print(f'测试用户注册失败: {response.status_code}, {response.text}')
        return False


# 直接使用UserService进行登录
def login(user=None):
    try:
        # 导入create_app函数和UserService
        from app import create_app
        from app.services.user.user_service import UserService
        
        # 创建应用实例
        app = create_app()
        
        # 创建应用上下文
        with app.app_context():
            # 如果提供了用户参数，则使用该用户登录
            if user is None:
                user = TEST_USER
            
            # 调用UserService的login方法
            user_obj, access_token, refresh_token, request_id, error = UserService.login(
                user['username'], user['password']
            )
            
            if error:
                print(f'登录失败: {error}')
                return None, None
            else:
                print('登录成功，获取令牌')
                return access_token, refresh_token
    except Exception as e:
        print(f'登录过程中出错: {str(e)}')
        return None, None

# 测试受保护路由
def test_protected_route(access_token):
    try:
        # 导入create_app函数
        from app import create_app
        from flask_jwt_extended import decode_token
        
        # 创建应用实例和上下文
        app = create_app()
        with app.app_context():
            # 解码令牌获取用户ID
            decoded_token = decode_token(access_token)
            user_id = decoded_token['sub']
            print(f'令牌有效，用户ID: {user_id}')
            return True
    except Exception as e:
        print(f'令牌验证失败: {str(e)}')
        return False

# 原始API验证方法（保留）
def test_protected_route_api(access_token):
    url = f'{BASE_URL}/user/profile'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('API验证通过')
        return True
    else:
        print(f'API验证失败: {response.status_code}, {response.text}')
        return False

# 刷新令牌
def refresh_token(refresh_token):
    url = f'{BASE_URL}/auth/refresh'
    headers = {'Authorization': f'Bearer {refresh_token}'}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f'刷新令牌失败: {response.status_code}, {response.text}')
        return None

# 主测试函数
def main(use_admin=False):
    print('开始测试登录超时问题...')

    # 登录获取令牌
    if use_admin:
        print('使用管理员账号登录...')
        access_token, refresh_token = login(ADMIN_USER)
    else:
        # 注册测试用户
        if not register_test_user():
            print('无法创建测试用户，测试终止')
            return

        # 登录获取令牌
        access_token, refresh_token = login()

    if not access_token or not refresh_token:
        print('无法获取令牌，测试终止')
        return

    print('登录成功，获取到令牌')
    print(f'访问令牌长度: {len(access_token)}')
    print(f'刷新令牌长度: {len(refresh_token)}')

    # 测试令牌有效性
    if test_protected_route(access_token):
        print('初始令牌验证通过')
    else:
        print('初始令牌验证失败')
        return

    # 监控令牌过期情况
    print('开始监控令牌过期情况...')
    max_test_time = 3600  # 测试1小时
    check_interval = 30    # 每30秒检查一次
    token_valid = True
    elapsed_time = 0

    while token_valid and elapsed_time < max_test_time:
        time.sleep(check_interval)
        elapsed_time += check_interval

        # 检查令牌是否有效
        token_valid = test_protected_route(access_token)

        if token_valid:
            print(f'令牌仍然有效，已过去 {elapsed_time} 秒')
        else:
            print(f'令牌已过期，共持续 {elapsed_time} 秒')

            # 尝试刷新令牌
            new_access_token = refresh_token(refresh_token)
            if new_access_token:
                access_token = new_access_token
                token_valid = True
                print(f'令牌刷新成功，新访问令牌长度: {len(access_token)}')
            else:
                print('无法刷新令牌，测试终止')
                break

    if elapsed_time >= max_test_time:
        print(f'测试完成，令牌在 {max_test_time} 秒内未过期')

if __name__ == '__main__':
    # 默认使用管理员账号登录
    main(use_admin=True)