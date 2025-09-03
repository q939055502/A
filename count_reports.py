from app import create_app
from app.models.report.inspection_report import InspectionReport
from app.db import db

app = create_app()

with app.app_context():
    # 查询报告表总数据量
    total_reports = db.session.query(InspectionReport).count()
    
    # 查询未被删除的报告数据量
    active_reports = db.session.query(InspectionReport).filter_by(is_deleted=False).count()
    
    print(f"报告表总数据量: {total_reports}")
    print(f"未被删除的报告数据量: {active_reports}")
    
    # 可以根据需要添加更多查询条件，例如按状态查询
    pending_reports = db.session.query(InspectionReport).filter_by(report_status='pending', is_deleted=False).count()
    print(f"状态为'pending'的报告数据量: {pending_reports}")