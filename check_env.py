import os
# 查看所有环境变量
print("环境变量列表：")
for key, value in os.environ.items():
    print(f"{key}={value}")

# 查看特定的DATABASE_URL环境变量
database_url = os.environ.get('DATABASE_URL')
print(f"\nDATABASE_URL = {database_url}")