"""时间工具模块
提供与时间相关的工具函数，包括时间戳生成、时间字符串与datetime对象的双向转换等。
"""
import time
from datetime import datetime
import re

def string_to_datetime(time_str, format_str=None):
    """
    将时间字符串转换为datetime对象

    Args:
        time_str (str): 时间字符串
        format_str (str, optional): 时间格式字符串。如果为None，将尝试自动匹配常用格式

    Returns:
        datetime: 转换后的datetime对象

    Raises:
        ValueError: 当时间字符串格式无效或无法匹配时
    """
    if not time_str:
        raise ValueError("时间字符串不能为空")

    # 如果未指定格式，尝试自动匹配常用格式
    if format_str is None:
        # 常用时间格式列表
        common_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]

        for fmt in common_formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue

        # 尝试匹配纯数字格式（如：202508131430）
        if re.match(r'^\d{12}$', time_str):
            try:
                return datetime.strptime(time_str, '%Y%m%d%H%M')
            except ValueError:
                pass
        elif re.match(r'^\d{8}$', time_str):
            try:
                return datetime.strptime(time_str, '%Y%m%d')
            except ValueError:
                pass

        # 尝试匹配中文日期格式（如：2025年8月13日）
        chinese_date_pattern = r'^(\d{4})年(\d{1,2})月(\d{1,2})日$'
        match = re.match(chinese_date_pattern, time_str)
        if match:
            year, month, day = match.groups()
            try:
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass

        # 尝试匹配带有时分的中文日期格式（如：2025年8月13日 14:30:00）
        chinese_datetime_pattern = r'^(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2}):(\d{1,2}):(\d{1,2})$'
        match = re.match(chinese_datetime_pattern, time_str)
        if match:
            year, month, day, hour, minute, second = match.groups()
            try:
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            except ValueError:
                pass

        raise ValueError(f"无法将时间字符串 '{time_str}' 转换为datetime对象，不支持的格式")
    else:
        try:
            return datetime.strptime(time_str, format_str)
        except ValueError as e:
            raise ValueError(f"时间格式错误: {e}")

def datetime_to_string(dt_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """将datetime对象转换为字符串

    Args:
        dt_obj (datetime): datetime对象
        format_str (str): 时间格式字符串，默认为 '%Y-%m-%d %H:%M:%S'

    Returns:
        str: 转换后的时间字符串

    Raises:
        TypeError: 当输入不是datetime对象时
        ValueError: 当格式字符串无效时
    """
    if not isinstance(dt_obj, datetime):
        raise TypeError("输入必须是datetime对象")

    # 移除了额外的格式验证逻辑，依靠datetime.strftime()自身的异常处理
    
    try:
        return dt_obj.strftime(format_str)
    except ValueError as e:
        raise ValueError(f"时间格式错误: {e}")

def get_timestamp():
    """生成时间戳（毫秒）

    生成当前时间的毫秒级时间戳，
    用于API响应中的时间标记和事件排序。

    Returns: 
        int: 当前时间的毫秒级时间戳
    """
    return int(time.time() * 1000)