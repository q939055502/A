# 认证工具
from datetime import  timedelta

import time
from flask import g
# 延迟导入，避免循环依赖
from flask_jwt_extended import JWTManager

# 在需要使用时再导入其他函数
# 注意：这些导入需要在函数内部进行，而不是在模块级别
from flask_jwt_extended.utils import unset_jwt_cookies

from flask import current_app
from app.db import db
# 延迟导入TokenBlocklist，避免循环依赖
# from app.models.token import TokenBlocklist
from app.utils.logger import logger

# 延迟导入User模型，避免循环依赖
# from app.models.user import User
from app.utils.app_uuid import generate_request_id

jwt = JWTManager()

def generate_tokens(user_id, remember_me=False):
    """生成访问令牌和刷新令牌
    
    Args:
        user_id: 用户ID（将被转换为字符串）
        remember_me (bool, optional): 是否记住我. Defaults to False.
    
    Returns:
        tuple: (access_token, refresh_token)
    """
    # 延迟导入
    from flask_jwt_extended import create_access_token, create_refresh_token
    from flask import current_app
    
    # 确保用户ID是字符串类型
    user_id_str = str(user_id)
    logger.info(f"生成令牌: 用户ID={user_id} (类型: {type(user_id)}), 转换后={user_id_str}, remember_me={remember_me}")
    
    # 使用配置中的刷新令牌过期时间
    refresh_expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=3))
    logger.info(f"使用配置的刷新令牌过期时间: {refresh_expires_delta}")

    # 根据记住我状态调整刷新令牌过期时间
    if remember_me:
        # 记住我状态下，刷新令牌过期时间延长为配置值的2倍
        refresh_expires_delta = refresh_expires_delta * 2
        logger.info(f"记住我已启用，刷新令牌过期时间延长为: {refresh_expires_delta}")
    
    # 获取配置中的访问令牌过期时间
    access_expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=30))
    logger.info(f"使用配置的访问令牌过期时间: {access_expires_delta}")
    
    try:
        # 生成令牌，将记住我状态添加到令牌声明中
        access_token = create_access_token(
            identity=user_id_str,
            additional_claims={'remember_me': remember_me},
            expires_delta=access_expires_delta  # 使用配置的过期时间
        )
        refresh_token = create_refresh_token(
            identity=user_id_str,
            expires_delta=refresh_expires_delta,
            additional_claims={'remember_me': remember_me}
        )

        logger.info(f"令牌生成成功: access_token长度={len(access_token)}, refresh_token长度={len(refresh_token)}")
        return access_token, refresh_token
    except Exception as e:
        logger.error(f"令牌生成失败: {str(e)}, 用户ID={user_id_str}, remember_me={remember_me}")
        raise


def block_token(jti):
    """将JWT令牌加入黑名单
    
    Args:
        jti (str): 令牌的唯一标识符
        
    Returns:
        bool: 操作是否成功
    """
    try:
        from datetime import datetime, timezone
        from app.models.token import TokenBlocklist
        
        # 将 jti 存入黑名单
        blocklist = TokenBlocklist(jti=jti, created_at=datetime.now(timezone.utc))
        db.session.add(blocklist)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"将令牌加入黑名单失败: {str(e)}")
        return False

def process_logout_token(token):
    """处理注销令牌
    
    Args:
        token (str): JWT令牌字符串
        
    Returns:
        bool: 操作是否成功
    """
    try:
        # 延迟导入
        from flask_jwt_extended import decode_token
        
        # 解码令牌以获取jti
        token_data = decode_token(token)
        jti = token_data['jti']
        
        # 调用block_token函数将令牌加入黑名单
        return block_token(jti)
    except Exception as e:
        logger.error(f"处理注销令牌时出错: {str(e)}")
        return False


def refresh_user_token(current_user, jwt_data):
    """刷新用户令牌
    
    Args:
        current_user: 当前用户标识（将被转换为字符串）
        jwt_data (dict): JWT完整载荷
    
    Returns:
        tuple: (new_access_token, new_refresh_token)
    """
    # 延迟导入
    from flask_jwt_extended import create_access_token, create_refresh_token
    from flask import current_app
    
    # 确保用户ID是字符串类型
    current_user_str = str(current_user)
    logger.info(f"刷新令牌: 用户标识={current_user} (类型: {type(current_user)}), 转换后={current_user_str}")
    
    # 检查原始令牌中是否有remember_me信息
    remember_me = jwt_data.get('remember_me', False)
    
    # 使用配置中的刷新令牌过期时间
    refresh_expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=3))
    logger.info(f"使用配置的刷新令牌过期时间: {refresh_expires_delta}")

    # 根据记住我状态调整刷新令牌过期时间
    if remember_me:
        # 记住我状态下，刷新令牌过期时间延长为配置值的2倍
        refresh_expires_delta = refresh_expires_delta * 2
        logger.info(f"记住我已启用，刷新令牌过期时间延长为: {refresh_expires_delta}")
    
    # 获取配置中的访问令牌过期时间
    access_expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(minutes=30))
    logger.info(f"使用配置的访问令牌过期时间: {access_expires_delta}")
    
    # 创建新的访问令牌和刷新令牌
    new_token = create_access_token(
        identity=current_user_str,
        fresh=False,  # 非新鲜令牌，不可用于敏感操作
        expires_delta=access_expires_delta  # 使用配置的过期时间
    )
    new_refresh_token = create_refresh_token(
        identity=current_user_str,
        expires_delta=refresh_expires_delta,
        additional_claims={'remember_me': remember_me}  # 保持记住我状态
    )
    
    logger.info(f"令牌刷新成功: new_access_token长度={len(new_token)}, new_refresh_token长度={len(new_refresh_token)}")
    return new_token, new_refresh_token



# 注册JWT令牌黑名单检查器
# 此装饰器会使Flask-JWT-Extended在验证令牌时自动调用该函数
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    # 调用check_token_in_blocklist函数检查令牌是否在黑名单中
    # jwt_header: JWT头部信息
    # jwt_payload: JWT负载信息
    return check_token_in_blocklist(jwt_header, jwt_payload)

def check_token_in_blocklist(jwt_header, jwt_payload):
    """检查令牌是否在黑名单中
    
    Args:
        jwt_header (dict): JWT头部
        jwt_payload (dict): JWT载荷
        
    Returns:
        bool: 是否在黑名单中
    """
    from app.models.token import TokenBlocklist
    jti = jwt_payload["jti"]  # 获取令牌唯一标识
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None  # 存在则返回True（表示被拉黑）


def handle_refresh():
    """处理令牌刷新逻辑
    
    Returns:
        tuple: (success, new_access_token, new_refresh_token, message) 操作是否成功、新的访问令牌、新的刷新令牌及消息
    """
    try:
        # 延迟导入
        from flask_jwt_extended import get_jwt_identity, get_jwt
        
        # 获取当前用户标识和JWT完整载荷
        current_user = get_jwt_identity()
        jwt_data = get_jwt()
        
        # 获取当前刷新令牌的jti
        current_refresh_jti = jwt_data['jti']
        
        # 刷新令牌
        new_access_token, new_refresh_token = refresh_user_token(current_user, jwt_data)
        
        # 将旧的刷新令牌加入黑名单
        from app.models.token import TokenBlocklist
        from datetime import datetime, timedelta
        
        # 获取令牌过期时间
        exp_timestamp = jwt_data['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # 创建TokenBlocklist记录
        token_block = TokenBlocklist(
            jti=current_refresh_jti,
            created_at=datetime.utcnow()
        )
        
        # 添加到数据库
        from app.db import db
        db.session.add(token_block)
        db.session.commit()
        logger.info(f"旧刷新令牌已加入黑名单: {current_refresh_jti}")
        
        return True, new_access_token, new_refresh_token, "令牌刷新成功"
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        return False, None, None, f"令牌刷新失败: {str(e)}"
# 移除整个verify_user_login函数

