from flask_jwt_extended import jwt_required
from app.models.report.inspection_report import InspectionReport
from app.models.user.user import User  # 添加User模型导入
from app.services.permission_service import PermissionService  # 添加PermissionService导入
import logging
import re
from datetime import datetime, timezone
from flask import request, g, Blueprint
from app.utils.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND
)
from app.utils.response import api_response, handle_exception, generate_request_id
from app.services.report.report_service import ReportService
from app.utils.report_schemas import ReportUpdate
from pydantic import ValidationError
from app import db
from app.utils.auth import permission_required, get_current_user

report_bp = Blueprint('report_bp', __name__, url_prefix='/report')  # Confirmed correct URL prefix as required

@report_bp.route('/get-all-reports', methods=['GET'])
@jwt_required()
@permission_required('inspection_report', 'view', 'own')
def get_all_reports():
    try:
        result = ReportService.get_all_reports()
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data=result
        )
    except Exception as e:
        logging.error(f"Error in /report/get-all-reports: {str(e)}")
        return handle_exception(e, '获取报告列表失败')



@report_bp.route('/get-reports', methods=['GET'])
@jwt_required()
@permission_required('inspection_report', 'view', scope='own')  # 移除固定的'own'范围
def get_reports():
    try:
        page = request.args.get('page', 1, type=int)#当前页码
        per_page = request.args.get('per_page', 10, type=int)#每页数量
        search_keyword = request.args.get('search_keyword', '', type=str)

        # 获取当前用户ID
        user_id = g.user_id

        # 检查用户是否拥有'inspection_report'的'view'权限且范围为'all'
        user = User.query.get(user_id)
        has_all_permission = PermissionService.has_user_permission(
            user, 'inspection_report', 'view', 'all'
        )

        # 根据权限范围确定是否需要过滤
        scope = 'all' if has_all_permission else 'own'

        result = ReportService.get_reports_paginated(
            page, per_page, search_keyword, user_id=user_id, scope=scope
        )

        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data=result
        )
    except Exception as e:
        logging.error(f"Error in /report/get-reports: {str(e)}")
        return handle_exception(e, '获取报告列表失败')


@report_bp.route('/get-report-by-code', methods=['GET'])
def get_report_by_code():
    try:
        report_code = request.args.get('report_code', '', type=str)
        if not report_code:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='报告编号不能为空'
            )
        result = ReportService.get_report_by_code(report_code)
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
                code=HTTP_404_NOT_FOUND,
                message=result['message']
            )
    except Exception as e:
        logging.error(f"Error in /report/get-report-by-code: {str(e)}")
        return handle_exception(e, '获取报告详情失败')


@report_bp.route('/get-total-active-reports', methods=['GET'])
def get_total_active_reports():
    try:
        total_count = ReportService.get_total_active_reports_count()
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='操作成功',
            data={'total_count': total_count}
        )
    except Exception as e:
        logging.error(f"Error in /report/get-total-active-reports: {str(e)}")
        return handle_exception(e, '获取有效报告总数失败')


@report_bp.route('/search', methods=['GET'])
@jwt_required()
@permission_required('inspection_report', 'view', 'own')
def search_reports():
    try:
        search_param = request.args.get('search_keyword', '', type=str)

        # 调用服务层方法搜索报告
        result = ReportService.search_reports(search_param)

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
                code=result.get('code', 400),
                message=result['message'],
                data=result.get('data', {})
            )
    except Exception as e:
        logging.error(f"Error in /report/search: {str(e)}")
        return handle_exception(e, '搜索报告失败')


@report_bp.route('/delete-report/<report_code>', methods=['DELETE'])
@jwt_required()
@permission_required('inspection_report', 'delete', 'own', resource_id_param='report_code')
def delete_report(report_code):
    try:
        result = ReportService.soft_delete_report(report_code)
        if result['success']:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message='报告删除成功',
                data={}
            )
        else:
            return api_response(
                success=False,
                code=HTTP_404_NOT_FOUND,
                message=result['message'],
                data={}
            )
    except Exception as e:
        logging.error(f"Error in /report/delete-report: {str(e)}")
        return handle_exception(e, '删除报告失败')


@report_bp.route('/add-report', methods=['POST'])
@jwt_required()
@permission_required('inspection_report', 'create', 'all')
def add_report():
    
    try:
        data = request.json
        # 过滤掉updated_at和created_at字段
        filtered_data = {k: v for k, v in data.items() if k not in ['updated_at', 'created_at']}
        data = filtered_data

        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空',
                data={}
            )

        # 获取当前登录用户ID
        user_id = getattr(g, 'user_id', None)

        print('user_id', user_id)
        if not user_id:
            return api_response(
                success=False,
                code=HTTP_401_UNAUTHORIZED,
                message='未认证，请先登录',
                data={}
            )

        # 调用服务层方法创建报告
        result = ReportService.create_report(data, user_id)

        if result['success']:
            return api_response(
                success=True,
                code=result['code'],
                message=result['message'],
                data={
                    'report': result['data'],
                    'code': result['code'],
                    'message': result['message'],
                    'report_status': result['data']['report_status']
                }
            )
        else:
            return api_response(
                success=False,
                code=result.get('code', 400),
                message=result['message'],
                data={}
            )
    except Exception as e:
        logging.error(f"Error in /report/add-report: {str(e)}")
        return handle_exception(e, '添加报告失败')


@report_bp.route('/update-report/<string:report_code>', methods=['PUT'])
@jwt_required()
@permission_required('inspection_report', 'edit', 'own', resource_id_param='report_code')
def update_report(report_code):
    try:
        
        data = request.json
        # 过滤掉updated_at和created_at字段
        filtered_data = {k: v for k, v in data.items() if k not in ['updated_at', 'created_at']}
        data = filtered_data
        
        if not data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空',
                data={}
            )
        
        try:
            # 使用Pydantic模型验证数据
            validated_data = ReportUpdate(**data).dict()
            
            # 打印验证后的字段名
            print("验证后的字段名:")
            for field_name in validated_data.keys():
                if field_name not in ['updated_at', 'created_at'] and validated_data[field_name] is not None:
                    print(f"- {field_name}")
            # 获取当前用户ID
            current_user = get_current_user()
            user_id = str(current_user.id)

            # 调用服务层方法更新报告
            result = ReportService.update_report(report_code, validated_data, user_id)
        except ValidationError as e:
            # 处理验证错误
            errors = e.errors()
            error_messages = []
            for error in errors:
                field = error.get('loc', ['unknown'])[0]
                message = error.get('msg', '验证失败')
                error_messages.append(f'{field}: {message}')
            
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message="数据验证失败",
                data={'errors': error_messages}
            )
        
        if result['success']:
            return api_response(
                success=True,
                code=HTTP_200_OK,
                message='报告更新成功',
                data={'report': result['data']}
            )
        else:
            return api_response(
                success=False,
                code=result.get('code', HTTP_404_NOT_FOUND),  # 使用服务层返回的状态码,
                message=result['message'],
                data={}
            )
    except Exception as e:
        logging.error(f"Error in /report/update-report/{report_code}: {str(e)}")
        return handle_exception(e, '更新报告失败')


@report_bp.route('/batch-delete-reports', methods=['POST'])
@jwt_required()
@permission_required('inspection_report', 'delete', 'own', resource_id_param='report_code')
def batch_delete_reports():
    try:
        data = request.json
        if not data or 'report_codes' not in data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求数据不能为空，且必须包含report_codes字段',
                data={}
            )

        report_codes = data['report_codes']
        if not isinstance(report_codes, list) or len(report_codes) == 0:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='report_codes必须是非空列表',
                data={}
            )

        result = ReportService.batch_soft_delete_reports(report_codes)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message=result['message'],
            data={
                'total_count': result['data']['total_count'],
                'success_count': result['data']['success_count'],
                'failed_count': result['data']['failed_count'],
                'failed_reports': result['data']['failed_reports']
            }
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in /report/batch-delete-reports: {str(e)}")
        return handle_exception(e, '批量删除报告失败')


@report_bp.route('/batch-add-reports', methods=['POST'])
@jwt_required()
@permission_required('inspection_report', 'create', 'own')
def batch_create_reports():
    try:
        data = request.json
        if not data or 'reports_data' not in data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数错误，缺少reports_data字段',
                data={}
            )
        
        reports_data = data['reports_data']
        if not isinstance(reports_data, list) or len(reports_data) == 0:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='reports_data必须是非空数组格式',
                data={}
            )
        
        # 检查每个报告数据是否包含必填字段
        required_fields = ['report_code', 'project_name', 'client_unit', 'inspection_unit', 'inspection_object', 'inspection_type', 'inspection_conclusion']
        for idx, report_data in enumerate(reports_data):
            missing_fields = [field for field in required_fields if field not in report_data or not report_data[field]]
            if missing_fields:
                return api_response(
                    success=False,
                    code=HTTP_400_BAD_REQUEST,
                    message=f'第{idx+1}个报告数据缺少必填字段: {", ".join(missing_fields)}',
                    data={}
                )
        
        # 获取当前用户ID
        user_id = getattr(g, 'user_id', None)
        if not user_id:
            return api_response(
                success=False,
                code=HTTP_401_UNAUTHORIZED,
                message='未认证，请先登录',
                data={}
            )
        
        result = ReportService.batch_create_reports(reports_data, user_id)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message=result['message'],
            data={
                'total_count': result['data']['total_count'],
                'success_count': result['data']['success_count'],
                'failed_count': result['data']['failed_count'],
                'failed_reports': result['data']['failed_reports']
            }
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in /report/api/reports/batch: {str(e)}")
        return handle_exception(e, '批量创建报告失败')


@report_bp.route('/batch-update-reports', methods=['PUT'])
@jwt_required()
@permission_required('inspection_report', 'edit', 'own')
def batch_update_reports():
    try:
        data = request.json
        # print(data)
        if not data or 'reports_data' not in data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数错误，缺少reports_data字段',
                data={}
            )
        
        reports_data = data['reports_data']
        if not isinstance(reports_data, list) or len(reports_data) == 0:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='reports_data必须是非空数组格式',
                data={}
            )
        
        # 检查每个报告数据是否包含report_code
        for idx, report_data in enumerate(reports_data):
            if 'report_code' not in report_data or not report_data['report_code']:
                return api_response(
                    success=False,
                    code=HTTP_400_BAD_REQUEST,
                    message=f'第{idx+1}个报告数据缺少report_code字段',
                    data={}
                )
            
            # 过滤掉updated_at和created_at字段
            filtered_data = {k: v for k, v in report_data.items() if k not in ['updated_at', 'created_at']}
            reports_data[idx] = filtered_data
        
        # 获取当前用户ID
        current_user = get_current_user()
        user_id = str(current_user.id)
        
        result = ReportService.batch_update_reports(reports_data, user_id)
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message=result['message'],
            data={
                'total_count': result['data']['total_count'],
                'success_count': result['data']['success_count'],
                'failed_count': result['data']['failed_count'],
                'failed_reports': result['data']['failed_reports']
            }
        )
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in /report/api/reports/batch (PUT): {str(e)}")
        return handle_exception(e, '批量更新报告失败')


@report_bp.route('/get-reports-by-codes', methods=['POST'])
@jwt_required()
@permission_required('inspection_report', 'view', 'own')
def get_reports_by_codes():
    try:
        data = request.json
        if not data or 'report_codes' not in data:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='请求参数错误，缺少report_codes字段',
                data={}
            )
        
        report_codes = data['report_codes']
        if not isinstance(report_codes, list) or len(report_codes) == 0:
            return api_response(
                success=False,
                code=HTTP_400_BAD_REQUEST,
                message='report_codes必须是非空数组格式',
                data={}
            )
        
        # 获取当前用户ID
        current_user = get_current_user()
        user_id = str(current_user.id)
        
        # 检查用户是否拥有'inspection_report'的'view'权限且范围为'all'
        has_all_permission = PermissionService.has_user_permission(
            current_user, 'inspection_report', 'view', 'all'
        )
        
        # 根据权限获取报告数据
        result = ReportService.get_reports_by_codes(report_codes, user_id, has_all_permission)
        
        return api_response(
            success=True,
            code=HTTP_200_OK,
            message='获取报告成功',
            data={
                'total_count': result['data']['total_count'],
                'success_count': result['data']['success_count'],
                'failed_count': result['data']['failed_count'],
                'reports': result['data']['reports'],
                'failed_codes': result['data']['failed_codes']
            }
        )
    except Exception as e:
        logging.error(f"Error in /report/get-reports-by-codes: {str(e)}")
        return handle_exception(e, '获取报告失败')