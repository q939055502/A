from flask import Blueprint, request
from app.services.admin.staff_service import StaffService
from app.utils.response import api_response
from app.utils.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from app.utils.schemas import StaffCreate, StaffUpdate, StaffRoleUpdate, StaffPermissionUpdate
from pydantic import ValidationError
from flask_jwt_extended import jwt_required
from app.utils.auth import permission_required

# 创建蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ---------------- 获取数据接口 (GET请求) ----------------


@admin_bp.route('/get_staff_list', methods=['GET'])
@jwt_required()
@permission_required('user', 'view', 'all')
def get_staff_list():
    """
    获取人员列表
    ---
    返回所有人员信息列表
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        keyword = request.args.get('keyword', '')
        status = request.args.get('status', type=int)
        role_id = request.args.get('role_id', type=int)

        # 调用服务层方法
        staff_list, total = StaffService.get_staff_list(
            page=page,
            per_page=per_page,
            keyword=keyword,
            status=status,
            role_id=role_id
        )

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取人员列表成功',
            data={
                'list': staff_list,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取人员列表失败: {str(e)}'
        )


@admin_bp.route('/get_staff_detail/<int:staff_id>', methods=['GET'])
@jwt_required()
@permission_required('user', 'view', 'all')
def get_staff_detail(staff_id):
    """
    获取人员详情
    ---
    根据ID获取指定人员的详细信息
    """
    try:
        staff = StaffService.get_staff_by_id(staff_id)
        
        if not staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取人员详情成功',
            data=staff
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取人员详情失败: {str(e)}'
        )


@admin_bp.route('/get_staff_role/<int:staff_id>', methods=['GET'])
@jwt_required()
@permission_required('user', 'role:manage', 'all')
def get_staff_role(staff_id):
    """
    获取人员角色
    ---
    获取指定人员的角色信息
    """
    try:
        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        # 调用服务层方法
        roles = StaffService.get_staff_roles(staff_id)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取人员角色成功',
            data=roles
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取人员角色失败: {str(e)}'
        )


@admin_bp.route('/get_staff_permissions/<int:staff_id>', methods=['GET'])
@jwt_required()
@permission_required('user', 'role:manage', 'all')
def get_staff_permissions(staff_id):
    """
    获取人员权限
    ---
    获取指定人员的所有权限
    """
    try:
        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        # 调用服务层方法
        permissions = StaffService.get_staff_permissions(staff_id)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取人员权限成功',
            data=permissions
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取人员权限失败: {str(e)}'
        )


@admin_bp.route('/get_role_list', methods=['GET'])
@jwt_required()
@permission_required('user', 'role:manage', 'all')
def get_role_list():
    """
    获取角色列表
    ---
    获取所有角色信息
    """
    try:
        # 调用服务层方法
        roles = StaffService.get_all_roles()

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取角色列表成功',
            data=roles
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取角色列表失败: {str(e)}'
        )


@admin_bp.route('/get_role_permissions/<int:role_id>', methods=['GET'])
@jwt_required()
@permission_required('user', 'permission:manage', 'all')
def get_role_permissions(role_id):
    """
    获取角色权限
    ---
    获取指定角色拥有的所有权限
    """
    try:
        # 调用服务层方法
        permissions = StaffService.get_role_permissions(role_id)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取角色权限成功',
            data=permissions
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取角色权限失败: {str(e)}'
        )


@admin_bp.route('/get_permissions_list', methods=['GET'])
@jwt_required()
@permission_required('system', 'permission:manage', 'all')
def get_permissions_list():
    """
    获取权限列表
    ---
    获取所有权限信息
    """
    try:
        # 调用服务层方法
        permissions = StaffService.get_permissions()

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取权限列表成功',
            data=permissions
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取权限列表失败: {str(e)}'
        )


@admin_bp.route('/get_all_roles_with_permissions', methods=['GET'])
@jwt_required()
@permission_required('system', 'permission:manage', 'all')
def get_all_roles_with_permissions():
    """
    获取所有角色及其权限
    ---
    获取系统中所有角色及其拥有的权限信息
    """
    try:
        # 调用服务层方法
        roles_with_permissions = StaffService.get_all_roles_with_permissions()

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取所有角色及其权限成功',
            data=roles_with_permissions
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'获取所有角色及其权限失败: {str(e)}'
        )


# ---------------- 更新数据接口 (POST/DELETE请求) ----------------


# 导入logger
from app.utils.logger import logger

@admin_bp.route('/create_staff', methods=['POST'])
@jwt_required()
@permission_required('user', 'create', 'all')  # 添加 'all' 作为 scope 参数
def create_staff():
    """
    创建新人员
    ---
    创建一个新的人员记录
    """
    try:
        data = request.get_json()
        print(data)

        # 使用Pydantic验证请求参数
        try:
            staff_data = StaffCreate(**data)
        except ValidationError as e:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数验证失败',
                data={'errors': e.errors()}
            )
        # 调用服务层方法
        try:
            # 直接传递StaffCreate对象，而不是model_dump()
            staff = StaffService.create_staff(staff_data)
        except Exception as service_e:
            logger.error(f'StaffService.create_staff 异常: {str(service_e)}', exc_info=True)
            return api_response(
                success=False,
                code=HTTP_500_INTERNAL_SERVER_ERROR,
                message=f'创建人员失败: {str(service_e)}'
            )

        return api_response(
            success=True,
            code=HTTP_201_CREATED,
            message='创建人员成功',
            data=staff
        )
    except Exception as e:
        logger.error(f'create_staff 路由异常: {str(e)}', exc_info=True)
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'创建人员失败: 服务器内部错误'
        )


@admin_bp.route('/update_staff/<int:staff_id>', methods=['POST'])
@jwt_required()
@permission_required('user', 'edit', 'all')
def update_staff(staff_id):
    """
    更新人员信息
    ---
    更新指定人员的信息
    """
    try:
        data = request.get_json()
        print(data)

        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )
        
        # 使用Pydantic验证请求参数
        try:
            staff_data = StaffUpdate(**data)
        except ValidationError as e:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数验证失败',
                data={'errors': e.errors()}
            )

        # 调用服务层方法
        updated_staff = StaffService.update_staff(staff_id, staff_data)
        
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='更新人员信息成功',
            data=updated_staff
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'更新人员信息失败: {str(e)}'
        )


@admin_bp.route('/update_staff_status', methods=['POST'])
@jwt_required()
@permission_required('user', 'edit', 'all')
def update_staff_status():
    """
    更新人员状态
    ---
    更新指定人员的状态 (1-正常、2-禁用)
    """
    try:
        data = request.get_json()
        staff_id = data.get('staff_id')
        status = data.get('status')

        if staff_id is None:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='缺少人员ID参数'
            )

        if status is None:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='缺少状态参数'
            )

        # 验证参数类型
        try:
            staff_id = int(staff_id)
            status = int(status)
        except ValueError:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='人员ID和状态参数必须是整数'
            )

        # 调用服务层方法
        updated_staff = StaffService.update_staff_status(staff_id, status)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='更新人员状态成功',
            data=updated_staff
        )
    except ValueError as e:
        return api_response(
            success=False,
            code=HTTP_400_BAD_REQUEST,
            message=str(e)
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'更新人员状态失败: {str(e)}'
        )


@admin_bp.route('/delete_staff/<int:staff_id>', methods=['DELETE'])
@jwt_required()
@permission_required('user', 'delete', 'all')
def delete_staff(staff_id):
    """
    删除人员
    ---
    删除指定的人员记录
    """
    try:
        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        # 调用服务层方法
        StaffService.delete_staff(staff_id)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='删除人员成功'
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'删除人员失败: {str(e)}'
        )


@admin_bp.route('/update_staff_roles/<int:staff_id>', methods=['POST'])
@jwt_required()
@permission_required('user', 'role:manage', 'all')
def update_staff_roles(staff_id):
    """
    更新人员角色
    ---
    更新指定人员的角色（替换现有角色）

    参数说明:
    - staff_id: 通过URL路径传递的人员ID，类型为整数
    - 请求体: JSON格式，包含role_ids字段（角色ID列表）

    前端传参示例:
    POST /update_staff_roles/123
    Content-Type: application/json
    {
      "role_ids": [1, 2, 3]
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空'
            )

        # 验证请求参数
        try:
            role_data = StaffRoleUpdate(**data)
        except ValidationError as e:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数验证失败',
                data={'errors': e.errors()}
            )

        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        # 调用服务层方法
        StaffService.update_staff_roles(staff_id, role_data.role_ids)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='更新人员角色成功'
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'更新人员角色失败: {str(e)}'
        )


        # 调用服务层方法
        StaffService.remove_staff_role(staff_id, role_id)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='移除人员角色成功'
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'移除人员角色失败: {str(e)}'
        )


@admin_bp.route('/update_staff_permissions/<int:staff_id>', methods=['POST'])
@jwt_required()
@permission_required('user', 'permission:manage', 'all')
def update_staff_permissions(staff_id):
    """
    更新人员权限
    ---
    为指定人员更新权限（替换现有权限）
    """
    try:
        data = request.get_json()

        # 使用Pydantic验证请求参数
        try:
            permission_data = StaffPermissionUpdate(**data)
        except ValidationError as e:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数验证失败',
                data={'errors': e.errors()}
            )

        # 检查人员是否存在
        existing_staff = StaffService.get_staff_by_id(staff_id)
        if not existing_staff:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message='人员不存在'
            )

        # 调用服务层方法
        StaffService.update_user_permissions(staff_id, permission_data.permission_ids)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='更新人员权限成功'
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'更新人员权限失败: {str(e)}'
        )


@admin_bp.route('/create_role', methods=['POST'])
@jwt_required()
@permission_required('system', 'role:manage', 'all')
def create_role():
    """
    创建角色
    ---
    创建一个新的角色
    """
    try:
        data = request.get_json()

        # 参数验证
        if 'name' not in data or not data['name']:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='角色名称是必填字段'
            )

        # 调用服务层方法
        role = StaffService.create_role(data)

        return api_response(
            success=True,
            code=HTTP_201_CREATED,
            message='创建角色成功',
            data=role
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'创建角色失败: {str(e)}'
        )


@admin_bp.route('/update_role_permissions/<int:role_id>', methods=['POST'])
@jwt_required()
@permission_required('system', 'permission:manage', 'all')
def update_role_permissions(role_id):
    """
    更新角色权限
    ---
    为指定角色添加或移除权限
    请求体格式: {
        "add_permission_ids": [1, 2, 3],  # 要添加的权限ID列表
        "remove_permission_ids": [4, 5]   # 要移除的权限ID列表
    }
    """
    try:
        data = request.get_json()
        add_permission_ids = data.get('add_permission_ids', [])
        remove_permission_ids = data.get('remove_permission_ids', [])

        # 调用服务层方法
        StaffService.update_role_permissions(role_id, add_permission_ids, remove_permission_ids)

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='更新角色权限成功'
        )
    except Exception as e:
        return api_response(
            success=False,
            code=HTTP_500_INTERNAL_SERVER_ERROR,
            message=f'更新角色权限失败: {str(e)}'
        )


# 注意：这里没有遗漏任何接口，所有接口都已按类别整理完毕


# 确保logger的导入位置正确，避免循环导入问题
# 如果有其他全局变量或配置，请在此处添加


# 蓝图注册到应用的操作通常在app/__init__.py中完成
# 此处仅定义蓝图和路由


# 可以在此添加其他辅助函数或工具函数
# 但建议将复杂的业务逻辑放在服务层处理