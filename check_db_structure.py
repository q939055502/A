import sqlite3

# 连接到数据库
conn = sqlite3.connect('instance/sample_db.sqlite')
cursor = conn.cursor()

# 查询表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='inspection_reports'")
result = cursor.fetchone()

if result:
    print("Table structure for inspection_reports:")
    print(result[0])
else:
    print("Table inspection_reports not found.")

# 查询announcements表结构
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='announcements'")
result = cursor.fetchone()

if result:
    print("Table structure for announcements:")
    print(result[0])
else:
    print("Table announcements not found.")

# 关闭连接
conn.close()