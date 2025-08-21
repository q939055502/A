from app import create_app
from app.models.user.user import User
from app.services.user.permission_service import PermissionService
from app.db import db

# 创建Flask应用实例
app = create_app()
# 创建应用上下文
app.app_context().push()

# 移除json模块导入，因为我们不再需要生成JSON文件
def get_all_users_with_permissions():
    # 查询所有用户
    users = User.query.all()
    result = []
    
    for user in users:
        # 获取用户权限
        permissions = PermissionService.get_user_permissions(user)
        
        # 整理用户信息和权限
        user_info = {
            'id': user.id,
            'username': user.username,
            'roles': [role.name for role in user.roles],
            'permissions': permissions,
            'email': user.email,
            'phone_number': user.phone_number
        }
        
        result.append(user_info)
    
    return result

def format_permission_string(permission):
    return f"{permission.resource}:{permission.action}:{permission.scope}"

def write_users_permissions_to_file(output_file):
    users_permissions = get_all_users_with_permissions()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("用户角色和权限分配结果\n")
        f.write("================================================================================\n")
        
        for user_info in users_permissions:
            # 用户基本信息
            f.write(f"用户: {user_info['username']} (ID: {user_info['id']})\n")
            
            # 角色信息
            roles_str = ', '.join(user_info['roles']) if user_info['roles'] else '无'
            f.write(f"  角色: {roles_str}\n")
            
            # 权限信息
            permissions = user_info['permissions']
            if permissions:
                permission_strs = [format_permission_string(perm) for perm in permissions]
                f.write(f"  通过角色获得的权限: {', '.join(permission_strs)}\n")
            else:
                f.write("  通过角色获得的权限: 无\n")
            
            # 额外分配的权限（当前没有直接分配的权限数据，暂时写无）
            f.write("  额外分配的权限: 无\n")
            
            # 分隔线
            f.write("--------------------------------------------------------------------------------\n")
    
    print(f"已将所有账号及其权限写入文件: {output_file}")

if __name__ == '__main__':
    output_file = 'd:/Projects/Python/A/docs/用户对应角色以及权限.txt'
    write_users_permissions_to_file(output_file)