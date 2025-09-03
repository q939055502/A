"""
安全工具模块，提供数据加密和解密功能
"""
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

# 从环境变量获取密钥和IV，如果不存在则使用默认值（实际生产环境应从环境变量或安全存储中获取）
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6').encode('utf-8')
ENCRYPTION_IV = os.environ.get('ENCRYPTION_IV', '1234567890abcdef').encode('utf-8')


def encrypt_data(data: str) -> str:
    """
    加密数据
    :param data: 要加密的字符串数据
    :return: 加密后的base64编码字符串
    """
    if not data:
        return ''

    # 确保密钥和IV长度符合AES要求
    key = ENCRYPTION_KEY.ljust(32, b'\0')[:32]  # AES-256需要32字节密钥
    iv = ENCRYPTION_IV.ljust(16, b'\0')[:16]    # AES需要16字节IV

    # 对数据进行PKCS7填充
    padder = padding.PKCS7(128).padder()
    data_bytes = data.encode('utf-8')
    padded_data = padder.update(data_bytes) + padder.finalize()

    # 创建AES加密器
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # 返回base64编码的加密数据
    return base64.b64encode(encrypted_data).decode('utf-8')


def decrypt_data(encrypted_data: str) -> str:
    """
    解密数据
    :param encrypted_data: 要解密的base64编码字符串
    :return: 解密后的字符串数据
    """
    if not encrypted_data:
        return ''

    # 确保密钥和IV长度符合AES要求
    key = ENCRYPTION_KEY.ljust(32, b'\0')[:32]
    iv = ENCRYPTION_IV.ljust(16, b'\0')[:16]

    # 解码base64加密数据
    encrypted_bytes = base64.b64decode(encrypted_data)

    # 创建AES解密器
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()

    # 去除PKCS7填充
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # 返回解密后的字符串
    return decrypted_data.decode('utf-8')
