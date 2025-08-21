import os
import sys
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.utils.jwt import generate_tokens
from flask_jwt_extended import decode_token

# 加载环境变量
os.environ['FLASK_ENV'] = 'development'

# 创建应用实例
app = create_app()

# 在应用上下文中测试令牌过期时间
with app.app_context():
    # 打印JWT配置
    print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
    
    # 生成令牌
    user_id = 1
    access_token, refresh_token = generate_tokens(user_id)
    print(f"生成的访问令牌: {access_token}")
    
    # 解码令牌以获取过期时间
    token_data = decode_token(access_token)
    exp_timestamp = token_data['exp']
    exp_time = datetime.fromtimestamp(exp_timestamp)
    now = datetime.now()
    
    # 计算令牌实际过期时间
    actual_expiry = exp_time - now
    print(f"令牌生成时间: {now}")
    print(f"令牌过期时间: {exp_time}")
    print(f"令牌实际过期时间: {actual_expiry}")
    
    # 验证令牌过期时间是否符合配置
    expected_expiry = app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=15))
    
    # 考虑到时间计算的微小差异，允许有10秒的误差
    if abs(actual_expiry.total_seconds() - expected_expiry.total_seconds()) < 10:
        print("令牌过期时间符合配置")
    else:
        print(f"令牌过期时间不符合配置: 预期{expected_expiry}, 实际{actual_expiry}")
        
    # 测试令牌在短时间内是否有效
    print("等待5秒后验证令牌是否有效...")
    time.sleep(5)
    try:
        # 再次解码令牌，如果未过期则不会抛出异常
        decode_token(access_token)
        print("5秒后令牌仍然有效")
    except Exception as e:
        print(f"5秒后令牌无效: {e}")
        
    # 注意：完整测试令牌过期需要等待30分钟，这里只测试短时间内的有效性
    print("测试完成。要完整测试30分钟过期时间，请保持脚本运行足够长时间。")