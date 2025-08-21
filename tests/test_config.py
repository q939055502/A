import os
from dotenv import load_dotenv
# 先加载环境变量
load_dotenv()

from config import Config

# 打印当前使用的配置类
print(f'当前配置类: {Config.__name__}')

# 打印数据库连接URL
print(f'数据库连接URL: {Config.SQLALCHEMY_DATABASE_URI}')

# 验证数据库文件路径是否正确
if 'sqlite:///' in Config.SQLALCHEMY_DATABASE_URI:
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    print(f'数据库文件路径: {db_path}')
    print(f'数据库文件是否存在: {os.path.exists(db_path)}')
else:
    print('不是SQLite数据库连接')