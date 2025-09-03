import secrets
print('生成JWT密钥')

# 生成JWT密钥
print(secrets.token_hex(32))
