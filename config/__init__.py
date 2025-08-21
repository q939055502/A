import os

import os

# 只导入开发环境配置类
from config.development import DevelopmentConfig


def get_config():
    """根据环境变量选择配置类

    作用: 根据FLASK_ENV环境变量的值选择对应的配置类
    返回: DevelopmentConfig或ProductionConfig类
    使用方法: 无需手动调用，应用会自动使用
    示例:
        - 当FLASK_ENV=development时，返回DevelopmentConfig
        - 当FLASK_ENV=production时，返回ProductionConfig
        - 未设置FLASK_ENV时，默认返回DevelopmentConfig
    """

    # print('------------------------环境变量---------------------------')
    # print(os.environ.get('FLASK_ENV', 'development'))
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        # 只在生产环境下导入ProductionConfig
        from config.production import ProductionConfig
        return ProductionConfig
    else:
        return DevelopmentConfig

# 创建配置对象
# 用途: 应用通过导入此对象来使用配置
# 使用方法: from config import Config
Config = get_config()
