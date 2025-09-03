# 命令包初始化文件

def init_commands(app):
    """初始化所有命令
    
    Args:
        app: Flask应用对象
    """
    try:
        from .init_permissions import register_command as register_init_permissions
        register_init_permissions(app)
    except ImportError as e:
        logger.error(f"导入并注册初始化权限命令失败: {e}")
    
    # 可以在这里添加其他命令的导入和注册
    # try:
    #     from .other_command import register_command as register_other_command
    #     register_other_command(app)
    # except ImportError as e:
    #     print(f"导入并注册其他命令失败: {e}")