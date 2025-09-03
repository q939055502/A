import pymysql
import os
from config import Config

print("尝试直接使用pymysql连接数据库...")

# 从配置中提取数据库连接信息
print(f"配置中的数据库URL: {Config.SQLALCHEMY_DATABASE_URI}")

# 直接尝试使用pymysql连接
try:
    # 尝试连接数据库
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='inspection_report',
        unix_socket='/tmp/mysql.sock',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("数据库连接成功!")
    
    # 执行一个简单的查询
    with connection.cursor() as cursor:
        sql = "SHOW TABLES"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(f"数据库中的表: {result}")
    
    connection.close()
    
except Exception as e:
    print(f"连接失败: {e}")