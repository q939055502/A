import os
from dotenv import load_dotenv
from app import create_app
from app.db import db
from app.models.report.inspection_report import InspectionReport

# 加载环境变量
load_dotenv()

def delete_latest_reports(count=1000):
    """删除检测报告表中最新的指定数量的数据"""
    app = create_app()
    
    with app.app_context():
        # 先查询最新的count条记录
        latest_reports = InspectionReport.query.order_by(InspectionReport.created_at.desc()).limit(count).all()
        
        if not latest_reports:
            print(f"未找到任何数据需要删除。")
            return
        
        # 显示要删除的数据信息
        print(f"将删除最新的{len(latest_reports)}条检测报告数据：")
        print(f"最早创建时间：{latest_reports[-1].created_at}")
        print(f"最晚创建时间：{latest_reports[0].created_at}")
        
        # 确认删除操作
        confirm = input("确认要删除这些数据吗？(y/n): ")
        if confirm.lower() != 'y':
            print("删除操作已取消。")
            return
        
        try:
            # 执行删除操作
            for report in latest_reports:
                db.session.delete(report)
            db.session.commit()
            print(f"成功删除了{len(latest_reports)}条检测报告数据。")
        except Exception as e:
            db.session.rollback()
            print(f"删除数据时发生错误：{str(e)}")

if __name__ == '__main__':
    delete_latest_reports(1000)