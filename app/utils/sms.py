"""
短信服务工具
用于发送短信验证码和其他短信通知
"""
import os
import random
import time
import logging
import redis
from flask import current_app

# 内存存储，用于Redis不可用的情况
memory_storage = {}

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

# 检查Redis连接状态的函数
def is_redis_available():
    try:
        return redis_client.ping()
    except:
        logger.error('Redis连接失败，将使用内存存储')
        return False

# 配置日志
logger = logging.getLogger(__name__)

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

# 短信验证码过期时间（秒）
SMS_CODE_EXPIRE = 300

# 短信发送间隔（秒）
SMS_SEND_INTERVAL = 60


def generate_sms_code(length=6):
    """生成指定长度的短信验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_sms(phone_number, template_param):
    """
    发送短信
    实际项目中，这里应该调用第三方短信服务API
    目前仅模拟发送
    """
    # 模拟短信发送
    logger.info(f"向手机 {phone_number} 发送短信，参数: {template_param}")

    # 实际项目中，这里应该调用短信服务提供商的API
    # 例如阿里云短信服务、腾讯云短信服务等
    # 以下是模拟代码
    # 检查是否在发送间隔内
    redis_available = is_redis_available()
    last_send_time = None
    
    if redis_available:
        last_send_time = redis_client.get(f'sms:last_send_time:{phone_number}')
    else:
        # 使用内存存储检查发送间隔
        if phone_number in memory_storage and 'last_send_time' in memory_storage[phone_number]:
            last_send_time = memory_storage[phone_number]['last_send_time']

    if last_send_time and float(last_send_time) + SMS_SEND_INTERVAL > time.time():
        remaining_time = int(float(last_send_time) + SMS_SEND_INTERVAL - time.time())
        return False, f'短信发送过于频繁，请 {remaining_time} 秒后再试'

    # 生成验证码
    code = generate_sms_code()
    logger.info(f"生成验证码: {code} 用于手机: {phone_number}")

    # 存储验证码
    current_time = time.time()
    if redis_available:
        # 存储到Redis
        redis_client.set(f'sms:code:{phone_number}', code, ex=SMS_CODE_EXPIRE)
        redis_client.set(f'sms:last_send_time:{phone_number}', str(current_time))
    else:
        # 存储到内存
        if phone_number not in memory_storage:
            memory_storage[phone_number] = {}
        memory_storage[phone_number]['code'] = code
        memory_storage[phone_number]['expire_time'] = current_time + SMS_CODE_EXPIRE
        memory_storage[phone_number]['last_send_time'] = current_time

    # 模拟发送成功
    return True, code


def verify_sms_code(phone_number, code):
    """验证短信验证码"""
    redis_available = is_redis_available()
    stored_code = None
    current_time = time.time()

    if redis_available:
        # 从Redis获取验证码
        stored_code = redis_client.get(f'sms:code:{phone_number}')
    else:
        # 从内存存储获取验证码
        if phone_number in memory_storage and 'code' in memory_storage[phone_number]:
            # 检查是否过期
            if memory_storage[phone_number]['expire_time'] > current_time:
                stored_code = memory_storage[phone_number]['code']
            else:
                # 过期则删除
                del memory_storage[phone_number]['code']

    if not stored_code:
        return False, '验证码已过期'

    # 比较验证码
    if isinstance(stored_code, bytes):
        stored_code = stored_code.decode()
    if stored_code != code:
        return False, '验证码错误'

    # 验证成功后删除验证码
    if redis_available:
        redis_client.delete(f'sms:code:{phone_number}')
    else:
        if phone_number in memory_storage and 'code' in memory_storage[phone_number]:
            del memory_storage[phone_number]['code']

    return True, '验证成功'