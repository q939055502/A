from app.db import db
from app.models.announcement import Announcement
import logging
from app.utils.date_time import string_to_datetime, datetime_to_string

class AnnouncementService:
    @staticmethod
    def get_total_announcements_count():
        """获取数据库中公告的总条数(包含已删除)"""
        return Announcement.query.count()

    @staticmethod
    def get_total_active_announcements_count():
        """获取数据库中未软删除的公告总条数"""
        return Announcement.query.filter_by(is_deleted=False).count()

    @staticmethod
    def get_announcements_paginated(page=1, per_page=10, search_keyword=''):
        """分页获取公告

        Args:
            page (int): 当前页码
            per_page (int): 每页条数
            search_keyword (str): 搜索关键字

        Returns:
            dict: 包含公告列表和分页信息的字典
        """
        per_page = min(per_page, 1000)
        # 只查询未软删除的公告
        query = Announcement.query.filter_by(is_deleted=False)
        
        # 如果提供了搜索关键字，添加模糊查询条件
        if search_keyword:
            query = query.filter(
                db.or_(
                    Announcement.title.like(f'%{search_keyword}%'),
                    Announcement.content.like(f'%{search_keyword}%')
                )
            )
        
        pagination = query.order_by(
            Announcement.priority.desc(),  # 先按优先级降序排序（置顶的排前面）
            Announcement.created_at.desc()  # 再按创建时间降序排序
        ).paginate(page=page, per_page=per_page, error_out=False)
        announcements = [announcement.to_dict() for announcement in pagination.items]
        return {
            'announcements': announcements,
            'pagination': {
                'page': pagination.page,  # 当前页码
                'per_page': pagination.per_page,  # 每页条数
                'total_pages': pagination.pages,  # 总页数
                'total_items': pagination.total  # 搜索结果总条数
            }
        }

    @staticmethod
    def get_all_announcements():
        """获取所有未软删除的公告

        Returns:
            list: 公告字典列表
        """
        announcements = Announcement.query.filter_by(is_deleted=False).order_by(
            Announcement.priority.desc(),  # 先按优先级降序排序（置顶的排前面）
            Announcement.created_at.desc()  # 再按创建时间降序排序
        ).all()
        return [announcement.to_dict() for announcement in announcements]

    @staticmethod
    def create_announcement(announcement_data):
        """创建新公告

        Args:
            announcement_data (dict): 公告数据

        Returns:
            dict: 包含创建结果的字典
        """
        try:
            new_announcement = Announcement(
                title=announcement_data.get('title'),
                content=announcement_data.get('content'),
                icon=announcement_data.get('icon', ''),
                # 将is_pinned转换为priority值，100表示置顶，0表示普通
                priority=100 if announcement_data.get('is_pinned', False) else 0,
                is_active=announcement_data.get('is_active', True)
            )
            db.session.add(new_announcement)
            db.session.commit()
            return {
                'success': True,
                'message': '公告创建成功',
                'data': new_announcement.to_dict(),
                'code': 201
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"创建公告失败: {str(e)}")
            return {
                'success': False,
                'message': f'创建公告失败: {str(e)}',
                'code': 500
            }

    @staticmethod
    def soft_delete_announcement(announcement_id):
        """软删除公告：将公告标记为已删除但不实际从数据库中删除"""
        try:
            announcement = Announcement.query.get(announcement_id)
            if not announcement:
                return {
                    'success': False,
                    'message': '公告不存在',
                    'code': 404
                }

            announcement.is_deleted = True
            db.session.commit()
            return {
                'success': True,
                'message': '公告已成功删除',
                'code': 200
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"删除公告失败: {str(e)}")
            return {
                'success': False,
                'message': f'删除公告失败: {str(e)}',
                'code': 500
            }

    @staticmethod
    def get_announcement_by_id(announcement_id):
        """根据ID查询单条未软删除的公告数据"""
        announcement = Announcement.query.filter_by(id=announcement_id, is_deleted=False).first()
        if announcement:
            return {
                'success': True,
                'data': announcement.to_dict(),
                'code': 200
            }
        return {
            'success': False,
            'message': '未找到该公告或公告已被删除',
            'code': 404
        }

    @staticmethod
    def update_announcement(announcement_id, update_data):
        """更新公告信息

        Args:
            announcement_id (int): 公告ID
            update_data (dict): 要更新的数据

        Returns:
            dict: 包含更新结果的字典
        """
        try:
            announcement = Announcement.query.filter_by(id=announcement_id, is_deleted=False).first()
            if not announcement:
                return {
                    'success': False,
                    'message': '公告不存在或已被删除',
                    'code': 404
                }

            # 过滤掉不可修改的字段
            update_data = {k: v for k, v in update_data.items() if k not in ['id', 'created_at', 'updated_at']}

            # 更新字段
            for key, value in update_data.items():
                setattr(announcement, key, value)

            announcement.updated_at = datetime.utcnow()
            db.session.commit()
            return {
                'success': True,
                'message': '公告更新成功',
                'data': announcement.to_dict(),
                'code': 200
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"更新公告失败: {str(e)}")
            return {
                'success': False,
                'message': f'更新公告失败: {str(e)}',
                'code': 500
            }

    @staticmethod
    def get_latest_announcements(limit=10):
        """获取最新公告（按优先级和创建时间排序）

        Args:
            limit (int): 获取的公告数量，默认为10

        Returns:
            list: 最新公告的字典列表
        """
        announcements = Announcement.query.filter_by(is_deleted=False).order_by(
            Announcement.priority.desc(),  # 先按优先级降序排序（置顶的排前面）
            Announcement.created_at.desc()  # 再按创建时间降序排序
        ).limit(limit).all()
        return [announcement.to_dict() for announcement in announcements]

    @staticmethod
    def toggle_pin_announcement(announcement_id):
        """切换公告的置顶状态"""
        try:
            announcement = Announcement.query.filter_by(id=announcement_id, is_deleted=False).first()
            if not announcement:
                return {
                    'success': False,
                    'message': '公告不存在或已被删除',
                    'code': 404
                }

            # 使用priority字段实现置顶功能，100表示置顶，0表示取消置顶
            if announcement.priority >= 100:
                announcement.priority = 0
                is_pinned = False
            else:
                announcement.priority = 100
                is_pinned = True

            announcement.updated_at = datetime.utcnow()
            db.session.commit()
            return {
                'success': True,
                'message': f'公告已{"置顶" if is_pinned else "取消置顶"}',
                'data': announcement.to_dict(),
                'code': 200
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"切换公告置顶状态失败: {str(e)}")
            return {
                'success': False,
                'message': f'切换公告置顶状态失败: {str(e)}',
                'code': 500
            }

    @staticmethod
    def toggle_active_announcement(announcement_id):
        """切换公告的激活状态"""
        try:
            announcement = Announcement.query.filter_by(id=announcement_id, is_deleted=False).first()
            if not announcement:
                return {
                    'success': False,
                    'message': '公告不存在或已被删除',
                    'code': 404
                }

            announcement.is_active = not announcement.is_active
            announcement.updated_at = datetime.utcnow()
            db.session.commit()
            return {
                'success': True,
                'message': f'公告已{"激活" if announcement.is_active else "停用"}',
                'data': announcement.to_dict(),
                'code': 200
            }
        except Exception as e:
            db.session.rollback()
            logging.error(f"切换公告激活状态失败: {str(e)}")
            return {
                'success': False,
                'message': f'切换公告激活状态失败: {str(e)}',
                'code': 500
            }