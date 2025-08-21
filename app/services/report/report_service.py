from app.db import db
from app.models.report.inspection_report import InspectionReport
from app.models.user.user import User
import logging
import datetime
from app.utils.date_time import string_to_datetime, datetime_to_string

class ReportService:
    @staticmethod
    def get_total_reports_count():
        """获取数据库中检测报告的总条数(包含已删除)"""
        return InspectionReport.query.count()

    @staticmethod
    def get_total_active_reports_count():
        """获取数据库中未软删除的检测报告总条数"""
        return InspectionReport.query.filter_by(is_deleted=False).count()

    @staticmethod
    def get_reports_paginated(page=1, per_page=10, search_keyword=''):
        """分页获取检测报告

        Args:
            page (int): 当前页码
            per_page (int): 每页条数
            search_keyword (str): 搜索关键字

        Returns:
            dict: 包含报告列表和分页信息的字典
        """
        per_page = min(per_page, 1000)
        # 只查询未软删除的报告
        query = InspectionReport.query.filter_by(is_deleted=False)
        
        # 如果提供了搜索关键字，添加模糊查询条件
        if search_keyword:
            query = query.filter(
                db.or_(
                    InspectionReport.project_name.like(f'%{search_keyword}%'),
                    InspectionReport.report_code.like(f'%{search_keyword}%')
                )
            )
        
        pagination = query.order_by(
            InspectionReport.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        reports = [report.to_dict() for report in pagination.items]
        return {
            'reports': reports,
            'pagination': {
                'page': pagination.page,  # 当前页码
                'per_page': pagination.per_page,  # 每页条数
                'total_pages': pagination.pages,  # 总页数
                'total_items': pagination.total  # 搜索结果总条数
            }
        }

    @staticmethod
    def get_all_reports():
        """获取所有未软删除的报告

        Returns:
            list: 报告字典列表
        """
        reports = InspectionReport.query.filter_by(is_deleted=False).order_by(
            InspectionReport.created_at.desc()
        ).all()
        return [report.to_dict() for report in reports]

    # @staticmethod
    # def submit_report(report_data, user_id):
    #     """提交新报告

    #     Args:
    #         report_data (dict): 报告数据
    #         user_id (int): 关联的用户ID

    #     Returns:
    #         tuple: (报告对象或None, 错误信息或None)
    #     """
    #     try:
    #         # 检查用户是否存在
    #         user = User.query.get(user_id)
    #         if not user:
    #             return None, '关联的用户不存在'

    #         new_report = InspectionReport(
    #             project_name=report_data.get('project_name'),
    #             report_code=report_data.get('report_code'),
    #             client_unit=report_data.get('client_unit'),
    #             inspection_object=report_data.get('inspection_object'),
    #             inspection_conclusion=report_data.get('inspection_conclusion'),
    #             registrant=user.username  # 设置登记人为创建报告的用户账号
    #             # 可根据需要添加其他必要的报告字段
    #         )
    #         db.session.add(new_report)
    #         db.session.commit()
    #         return new_report, None
    #     except Exception as e:
    #         db.session.rollback()
    #         logging.error(f"提交报告失败: {str(e)}")
    #         return None, f'提交报告失败: {str(e)}'

    @staticmethod
    def associate_report_with_user(report_id, user_id):
        """将报告与用户关联

        Args:
            report_id (int): 报告ID
            user_id (int): 用户ID

        Returns:
            tuple: (是否成功, 错误信息或None)
        """
        try:
            report = InspectionReport.query.get(report_id)
            if not report:
                return False, '报告不存在'

            user = User.query.get(user_id)
            if not user:
                return False, '用户不存在'

            # 注意：InspectionReport模型中没有created_by字段，无法直接关联用户
            # 如需关联用户，建议在模型中添加user_id字段或创建关联表
            pass
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            logging.error(f"关联报告与用户失败: {str(e)}")
            return False, f'关联失败: {str(e)}'

    @staticmethod
    def soft_delete_report(report_code):
        """软删除报告：将报告标记为已删除但不实际从数据库中删除"""
        report = InspectionReport.query.filter_by(report_code=report_code).first()
        if report:
            report.is_deleted = True
            db.session.commit()
            return {'success': True, 'message': '报告已成功删除'}
        return {'success': False, 'message': '未找到该报告'}

    @staticmethod
    def batch_soft_delete_reports(report_codes):
        """批量软删除报告"""
        success_count = 0
        failed_count = 0
        failed_reports = []
        
        for code in report_codes:
            report = InspectionReport.query.filter_by(report_code=code).first()
            if report:
                report.is_deleted = True
                success_count += 1
            else:
                failed_count += 1
                failed_reports.append({'report_code': code, 'message': '未找到该报告'})
        
        db.session.commit()
        
        return {
            'success': True,
            'total_count': len(report_codes),
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_reports': failed_reports,
            'message': f'成功删除 {success_count} 个报告，失败 {failed_count} 个'
        }

    @staticmethod
    def get_report_by_code(report_code):
        """根据报告编号查询单条未软删除的报告数据"""
        report = InspectionReport.query.filter_by(report_code=report_code, is_deleted=False).first()
        if report:
            return {'success': True, 'data': report.to_dict()}
        return {'success': False, 'message': '未找到该报告或报告已被删除'}

    @staticmethod
    def update_report(report_code, update_data, user_id):
        """更新报告信息

        Args:
            report_code (str): 报告编号
            update_data (dict): 要更新的数据
            user_id (int): 当前登录用户ID

        Returns:
            dict: 包含更新结果的字典
        """
        
        try:
            # 查询报告
            # 尝试使用strip后的报告编号查询
            stripped_code = report_code.strip()
            report = InspectionReport.query.filter_by(report_code=stripped_code, is_deleted=False).first()
            if not report:
                return {'success': False, 'message': '报告不存在或已被删除', 'code': 404}
            
            # 报告编号不可修改，移除report_code字段(如果存在)
            if 'report_code' in update_data:
                del update_data['report_code']
            # 检查必填字段
            required_fields = ['project_name', 'client_unit', 'inspection_object', 'inspection_type', 'inspection_conclusion', 'inspection_unit']
            missing_fields = []
            
            for field in required_fields:
                if field not in update_data or not update_data[field]:
                    missing_fields.append(field)
            if missing_fields:
                return {'success': False, 'message': f'缺少必填字段: {missing_fields}', 'code': 400}

            # 日期字段列表，需要从模型定义中同步更新
            date_fields = ['commission_date', 'report_date', 'acceptance_date', 'sampling_date', 
                          'start_date', 'end_date', 'tester_date', 'review_date', 'approve_date', 'issue_date']
            # 日期时间字段列表
            datetime_fields = ['created_at']

            # 更新报告字段
            for key, value in update_data.items():
                if hasattr(report, key):
                    # 处理日期字段
                    if key in date_fields and value:
                        try:
                            # 检查value是否已经是datetime.date类型
                            if isinstance(value, datetime.date):
                                date_value = value
                            else:
                                # 假设日期格式为 'YYYY-MM-DD'
                                date_value = string_to_datetime(value, '%Y-%m-%d').date()
                            setattr(report, key, date_value)
                        except ValueError as ve:
                            return {'success': False, 'message': f'{key}日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
                    # 处理日期时间字段
                    elif key in datetime_fields and value:
                        try:
                            # 不指定格式，利用string_to_datetime函数的自动匹配功能
                            datetime_value = string_to_datetime(value)
                            setattr(report, key, datetime_value)
                        except ValueError as ve:
                            return {'success': False, 'message': f'{key}日期时间格式不正确，请使用YYYY-MM-DD HH:MM:SS格式', 'code': 400}
                    else:
                        setattr(report, key, value)
                else:
                    pass

            # 设置最后修改人和更新时间
            report.last_modified_by_id = int(user_id)
            report.updated_at = datetime.datetime.now(datetime.timezone.utc)
            
            db.session.commit()
            return {'success': True, 'message': '报告更新成功', 'data': report.to_dict(), 'code': 200}
        except Exception as e:
            db.session.rollback()
            logging.error(f"更新报告失败: {str(e)}")
            return {'success': False, 'message': f'更新报告失败: {str(e)}', 'code': 500}

    @staticmethod
    def create_report(report_data, user_id):
        """创建新报告

        Args:
            report_data (dict): 报告数据
            user_id (int): 当前登录用户ID

        Returns:
            dict: 包含创建结果的字典
        """
        try:
            # 检查用户是否存在
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'message': '用户不存在', 'code': 404}

            # 确保报告编号必须上传
            if 'report_code' not in report_data or not report_data['report_code']:
                return {'success': False, 'message': '报告编号必须上传', 'code': 400}

            # 检查报告编号是否已存在
            existing_report = InspectionReport.query.filter_by(report_code=report_data['report_code']).first()
            if existing_report:
                return {'success': False, 'message': '报告编号已存在', 'code': 400}

            # 解析日期字段
            # 委托日期解析
            commission_date_str = report_data.get('commission_date')
            if commission_date_str:
                try:
                    # 假设日期格式为 'YYYY-MM-DD'
                    commission_date = string_to_datetime(commission_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '委托日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                # 如果未提供委托日期，使用当前日期作为默认值
                commission_date = datetime.datetime.now(datetime.timezone.utc).date()

            # 受理日期解析
            acceptance_date_str = report_data.get('acceptance_date')
            if acceptance_date_str:
                try:
                    acceptance_date = string_to_datetime(acceptance_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '受理日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                acceptance_date = None

            # 抽样日期解析
            sampling_date_str = report_data.get('sampling_date')
            if sampling_date_str:
                try:
                    sampling_date = string_to_datetime(sampling_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '抽样日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                sampling_date = None

            # 开始日期解析
            start_date_str = report_data.get('start_date')
            if start_date_str:
                try:
                    start_date = string_to_datetime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '开始日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                start_date = None

            # 结束日期解析
            end_date_str = report_data.get('end_date')
            if end_date_str:
                try:
                    end_date = string_to_datetime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '结束日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                end_date = None

            # 检测完成日期解析
            tester_date_str = report_data.get('tester_date')
            if tester_date_str:
                try:
                    tester_date = string_to_datetime(tester_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '检测完成日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                tester_date = None

            # 审核日期解析
            review_date_str = report_data.get('review_date')
            if review_date_str:
                try:
                    review_date = string_to_datetime(review_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '审核日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                review_date = None

            # 批准日期解析
            approve_date_str = report_data.get('approve_date')
            if approve_date_str:
                try:
                    approve_date = string_to_datetime(approve_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '批准日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                approve_date = None

            # 签发日期解析
            issue_date_str = report_data.get('issue_date')
            if issue_date_str:
                try:
                    issue_date = string_to_datetime(issue_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return {'success': False, 'message': '签发日期格式不正确，请使用YYYY-MM-DD格式', 'code': 400}
            else:
                issue_date = None

            # 创建新报告
            # 获取当前时间（UTC时区）
            current_time = datetime.datetime.now(datetime.timezone.utc)

            new_report = InspectionReport(
                # 报告标识信息
                report_code=report_data['report_code'],  # 报告编号，唯一标识
                report_status=report_data.get('report_status', 'pending'),  # 报告状态，默认为待处理
                report_date=datetime.datetime.now(datetime.timezone.utc).date(),  # 报告日期
                qrcode_content=report_data.get('qrcode_content'),  # 二维码内容
                attachment_paths=report_data.get('attachment_paths'),  # 附件路径

                # 工程基本信息
                project_name=report_data['project_name'],  # 工程名称
                project_location=report_data.get('project_location'),  # 工程地址
                project_type=report_data.get('project_type'),  # 工程类型
                project_stage=report_data.get('project_stage'),  # 工程阶段
                construction_unit=report_data.get('construction_unit'),  # 建设单位
                contractor=report_data.get('contractor'),  # 施工单位
                supervisor=report_data.get('supervisor'),  # 监理单位
                witness_unit=report_data.get('witness_unit'),  # 见证单位
                remarks=report_data.get('remarks'),  # 备注

                # 委托与受理信息
                client_unit=report_data['client_unit'],  # 委托单位
                client_contact=report_data.get('client_contact'),  # 委托人
                acceptance_date=acceptance_date,  # 受理日期
                commission_date=commission_date,  # 委托日期
                commission_code=report_data.get('commission_code'),  # 委托编号
                salesperson=report_data.get('salesperson', ''),  # 业务员，默认为default_sales

                # 检测机构与资质
                inspection_unit=report_data['inspection_unit'],  # 检测单位
                certificate_no=report_data.get('certificate_no'),  # 资质证书编号
                contact_address=report_data.get('contact_address'),  # 联系地址
                contact_phone=report_data.get('contact_phone'),  # 联系电话
                

                # 检测对象与参数
                inspection_object=report_data['inspection_object'],  # 检测对象
                object_part=report_data.get('object_part'),  # 检测部位
                object_spec=report_data.get('object_spec'),  # 对象规格
                design_spec=report_data.get('design_spec'),  # 设计要求
                inspection_type=report_data['inspection_type'],  # 检验类型

                # 检测项目与结果
                inspection_items=report_data.get('inspection_items'),  # 检测项目
                test_items=report_data.get('test_items'),  # 检测项详情
                inspection_quantity=report_data.get('inspection_quantity'),  # 检测数量
                measurement_unit=report_data.get('measurement_unit'),  # 计量单位
                inspection_conclusion=report_data['inspection_conclusion'],  # 检测结论
                conclusion_description=report_data.get('conclusion_description'),  # 结论描述
                is_recheck=report_data.get('is_recheck', False),  # 是否复检，默认为否

                # 抽样与检测流程
                sampling_method=report_data.get('sampling_method'),  # 抽样方式
                sampling_date=sampling_date,  # 抽样日期
                sampler=report_data.get('sampler'),  # 抽样人员
                start_date=start_date,  # 开始日期
                end_date=end_date,  # 结束日期
                inspection_code=report_data.get('inspection_code'),  # 检测编号
                inspector=report_data.get('inspector'),  # 检测员
                tester_date=tester_date,  # 检测完成日期

                # 审批与归档
                reviewer=report_data.get('reviewer'),  # 审核人
                review_date=review_date,  # 审核日期
                approver=report_data.get('approver'),  # 批准人
                approve_date=approve_date,  # 批准日期
                issue_date=issue_date,  # 签发日期

                # 通用管理字段
                registrant_id=int(user_id),  # 登记人ID
                last_modified_by_id=int(user_id),  # 最后修改人ID
                updated_at=current_time  # 更新时间为当前时间
            )

            db.session.add(new_report)
            db.session.commit()

            return {
                'success': True,
                'message': '报告添加成功',
                'data': new_report.to_dict(),
                'code': 200
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"添加报告失败: {str(e)}")
            return {'success': False, 'message': f'添加报告失败: {str(e)}', 'code': 500}

    @staticmethod
    def search_reports(search_param):
        """搜索报告

        Args:
            search_param (str): 搜索参数

        Returns:
            dict: 包含搜索结果的字典
        """
        try:
            if not search_param:
                return {'success': False, 'message': '搜索参数不能为空', 'code': 400, 'data': {}}

            # 检测是否包含中文
            import re
            contains_chinese = bool(re.search(r'[\u4e00-\u9fa5]', search_param))

            # 根据是否包含中文选择查询字段
            if contains_chinese:
                # 按工程名称模糊查询（排除软删除的数据）
                reports = InspectionReport.query.filter(
                    InspectionReport.project_name.like(f'%{search_param}%')
                ).filter_by(is_deleted=False).all()
                # 按工程名称中查询字符串的位置排序
                def sort_by_match_degree(report):
                    return report.project_name.find(search_param)
            else:
                # 按报告编号模糊查询（排除软删除的数据）
                reports = InspectionReport.query.filter(
                    InspectionReport.report_code.like(f'%{search_param}%')
                ).filter_by(is_deleted=False).all()
                # 按报告编号中查询字符串的位置排序
                def sort_by_match_degree(report):
                    return report.report_code.find(search_param)

            reports_sorted = sorted(reports, key=sort_by_match_degree)

            # 转换为字典列表
            reports_dict = [report.to_dict() for report in reports_sorted]

            return {
                'success': True,
                'code': 200,
                'message': '操作成功',
                'data': {
                    'reports': reports_dict,
                    'total_count': len(reports_dict)
                }
            }
        except Exception as e:
            logging.error(f"搜索报告失败: {str(e)}")
            return {'success': False, 'message': f'搜索报告失败: {str(e)}', 'code': 500, 'data': {}}

