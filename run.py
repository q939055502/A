


import os
from dotenv import load_dotenv

# 先加载环境变量
load_dotenv()

# 调试环境变量
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
# 从配置中获取数据库连接信息
from config import Config
print(f"DATABASE_URL: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"当前配置类: {os.getenv('FLASK_ENV', 'development')}")

# 然后再导入app
from app import create_app
from app.db import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    # 从环境变量获取配置
    host = os.getenv('IP', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)