# """
# 遗留路由模块

# 功能: 包含已迁移至API蓝图的遗留路由定义，目前仅保留历史代码参考

# 主要接口:
# - GET /main/index: 已迁移至/api/reports的首页路由（兼容保留）

# 使用说明:
# - 所有路由需登录认证
# - 建议新功能直接使用/api前缀的接口
# - 返回格式为JSON
# """
# from flask import Blueprint, jsonify, request
# from flask_login import login_required, current_user
# from app.models import User, InspectionReport  # 导入用户模型和检测报告模型
# from app.db import db  # 导入数据库实例
# from app.routes.api_routes import api_bp



# # 创建名为 'main' 的蓝图（与登录重定向的 'main.index' 对应）
# main_bp = Blueprint('main', __name__, template_folder='../templates/main')

# @main_bp.route('/')  # 路由路径为根目录 '/'
# @login_required
# def index():
#     """首页视图函数，对应端点 'main.index'，展示检测报告列表"""
#     # 获取分页参数，默认为第1页
#     page = request.args.get('page', 1, type=int)
#     per_page = 10  # 每页显示10条记录

#     # 查询检测报告数据，按报告日期降序排列
#     pagination = InspectionReport.query.order_by(InspectionReport.report_date.desc()).paginate(
#         page=page, per_page=per_page, error_out=False
#     )
#     inspection_reports = pagination.items

#     # 渲染首页模板，传递变量到前端
#     return render_template('main/adminHomepage.html', inspection_reports=inspection_reports, pagination=pagination)
