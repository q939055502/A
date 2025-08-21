from flask_jwt_extended import jwt_required
import logging
from flask import request, g, Blueprint
from app.utils.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND
)
from app.utils.response import api_response, handle_exception
from app.services.announcement.announcement_service import AnnouncementService
from app.utils.auth import permission_required

announcement_bp = Blueprint('announcement_bp', __name__, url_prefix='/announcement')

@announcement_bp.route('/get-all', methods=['GET'])
@jwt_required()
@permission_required('announcement', 'view', 'all')
def get_all_announcements():
    try:
        result = AnnouncementService.get_all_announcements()
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data=result
        )
    except Exception as e:
        logging.error(f"Error in /announcement/get-all: {str(e)}")
        return handle_exception(e, '获取公告列表失败')

@announcement_bp.route('/get-paginated', methods=['GET'])
def get_announcements_paginated():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_keyword = request.args.get('search_keyword', '', type=str)

        result = AnnouncementService.get_announcements_paginated(page, per_page, search_keyword)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data=result
        )
    except Exception as e:
        logging.error(f"Error in /announcement/get-paginated: {str(e)}")
        return handle_exception(e, '获取公告列表失败')

@announcement_bp.route('/get-by-id/<int:announcement_id>', methods=['GET'])
def get_announcement_by_id(announcement_id):
    try:
        result = AnnouncementService.get_announcement_by_id(announcement_id)
        if result['success']:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message='操作成功',
                data=result['data']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/get-by-id: {str(e)}")
        return handle_exception(e, '获取公告详情失败')

@announcement_bp.route('/get-total-active', methods=['GET'])
def get_total_active_announcements():
    try:
        total_count = AnnouncementService.get_total_active_announcements_count()
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data={'total_count': total_count}
        )
    except Exception as e:
        logging.error(f"Error in /announcement/get-total-active: {str(e)}")
        return handle_exception(e, '获取有效公告总数失败')

@announcement_bp.route('/get-latest', methods=['GET'])
def get_latest_announcements():
    try:
        limit = request.args.get('limit', 10, type=int)
        result = AnnouncementService.get_latest_announcements(limit)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data=result
        )
    except Exception as e:
        logging.error(f"Error in /announcement/get-latest: {str(e)}")
        return handle_exception(e, '获取最新公告失败')

@announcement_bp.route('/create', methods=['POST'])
@jwt_required()
@permission_required('announcement', 'create', 'all')
def create_announcement():
    try:
        data = request.json
        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空'
            )

        # 调用服务层方法创建公告
        result = AnnouncementService.create_announcement(data)

        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message'],
                data=result['data']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/create: {str(e)}")
        return handle_exception(e, '创建公告失败')

@announcement_bp.route('/update/<int:announcement_id>', methods=['PUT'])
@jwt_required()
@permission_required('announcement', 'update', 'all')
def update_announcement(announcement_id):
    try:
        data = request.json
        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空'
            )

        # 调用服务层方法更新公告
        result = AnnouncementService.update_announcement(announcement_id, data)

        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message'],
                data=result['data']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/update: {str(e)}")
        return handle_exception(e, '更新公告失败')

@announcement_bp.route('/delete/<int:announcement_id>', methods=['DELETE'])
@jwt_required()
@permission_required('announcement', 'delete', 'all')
def delete_announcement(announcement_id):
    try:
        result = AnnouncementService.soft_delete_announcement(announcement_id)
        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/delete: {str(e)}")
        return handle_exception(e, '删除公告失败')

@announcement_bp.route('/toggle-pin/<int:announcement_id>', methods=['PATCH'])
@jwt_required()
@permission_required('announcement', 'update', 'all')
def toggle_pin_announcement(announcement_id):
    try:
        result = AnnouncementService.toggle_pin_announcement(announcement_id)
        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message'],
                data=result['data']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/toggle-pin: {str(e)}")
        return handle_exception(e, '切换公告置顶状态失败')

@announcement_bp.route('/toggle-active/<int:announcement_id>', methods=['PATCH'])
@jwt_required()
@permission_required('announcement', 'update', 'all')
def toggle_active_announcement(announcement_id):
    try:
        result = AnnouncementService.toggle_active_announcement(announcement_id)
        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message'],
                data=result['data']
            )
        else:
            return api_response(
                success=False,
                code=result['code'],
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /announcement/toggle-active: {str(e)}")
        return handle_exception(e, '切换公告激活状态失败')