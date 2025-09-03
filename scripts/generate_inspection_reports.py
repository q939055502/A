import random
import string
import datetime
import os
import sys
# 将项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from faker import Faker
from app import create_app  # 导入创建Flask应用的函数
from app.db import db
from app.models.report.inspection_report import InspectionReport

# 初始化Faker库，用于生成逼真的随机数据
fake = Faker('zh_CN')


def generate_random_report_code():
    """生成唯一的报告编号"""
    # 报告编号格式: REP-YYYYMMDD-随机6位字母数字
    date_part = datetime.datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"REP-{date_part}-{random_part}"


import json


def generate_inspection_report():
    """生成一个随机的检测报告对象"""
    # 随机日期生成
    today = datetime.date.today()
    max_days_before = 365  # 最大往前推365天
    
    def random_date():
        days_before = random.randint(0, max_days_before)
        return today - datetime.timedelta(days=days_before)
    
    # 生成报告
    report = InspectionReport(
        # 工程基本信息
        project_name=fake.company() + "工程",
        project_location=fake.address(),
        project_type=random.choice(["建筑工程", "市政桥梁", "公路工程", "水利工程"]),
        project_stage=random.choice(["地基基础", "主体结构", "装饰装修", "竣工验收"]),
        construction_unit=fake.company(),
        contractor=fake.company(),
        supervisor=fake.company(),
        witness_unit=fake.company(),
        remarks=fake.text(max_nb_chars=200),
        
        # 委托与受理信息
        client_unit=fake.company(),
        client_contact=fake.name(),
        acceptance_date=random_date(),
        commission_date=random_date(),
        commission_code=f"COMM-{random.randint(100000, 999999)}",
        salesperson=fake.name(),
        
        # 检测机构与资质
        inspection_unit="XX检测有限公司",
        certificate_no=f"JCZ-{random.randint(1000, 9999)}-{random.randint(2010, 2023)}",
        contact_address=fake.address(),
        contact_phone=fake.phone_number(),
        registrant=fake.name(),
        
        # 检测对象与参数
        inspection_object=random.choice(["混凝土结构", "钢结构", "地基基础", "防水材料"]),
        object_part=random.choice(["柱", "梁", "板", "墙", "基础"]),
        object_spec=f"{random.randint(100, 500)}mm×{random.randint(100, 500)}mm",
        design_spec=f"强度等级: C{random.randint(20, 50)}",
        inspection_type=random.choice(["常规检测", "专项检测", "见证检测"]),
        
        # 检测项目与结果
        inspection_items=random.choice(["混凝土强度", "钢筋保护层厚度", "回弹法检测", "超声波检测"]),
        test_items=random.choice(["大大", "小小", "查查"]),
        inspection_quantity=random.randint(1, 50),
        measurement_unit=random.choice(["个", "组", "点", "根"]),
        inspection_conclusion=random.choice(["合格", "不合格", "异常"]),
        conclusion_description=fake.text(max_nb_chars=200),
        is_recheck=random.choice([True, False]),
        
        # 抽样与检测流程
        sampling_method=random.choice(["随机抽样", "分层抽样", "系统抽样"]),
        sampling_date=random_date(),
        sampler=fake.name(),
        start_date=random_date(),
        end_date=random_date(),
        inspection_code=f"JC-{random.randint(100000, 999999)}",
        inspector=fake.name(),
        tester_date=random_date(),
        
        # 审批与归档
        reviewer=fake.name(),
        review_date=random_date(),
        approver=fake.name(),
        approve_date=random_date(),
        report_date=random_date(),
        issue_date=random_date(),
        
        # 报告管理与附件
        report_code=generate_random_report_code(),
        report_status=random.choice(["pending", "approved", "rejected", "issued"]),
        qrcode_content=f"https://example.com/report/{random.randint(1000000, 9999999)}",
        attachment_paths=[f"attachments/report_{random.randint(1000000, 9999999)}.pdf"]
    )
    
    return report


def batch_insert_reports(count=500):
    """批量插入检测报告数据"""
    reports = []
    for _ in range(count):
        reports.append(generate_inspection_report())
    
    # 批量插入
    db.session.bulk_save_objects(reports)
    db.session.commit()
    print(f"成功插入 {count} 条检测报告数据")


if __name__ == "__main__":
    # 提示用户安装必要的依赖
    print("请确保已安装faker库: pip install faker")
    print("正在生成1000条检测报告数据...")
    # 创建Flask应用和应用上下文
    app = create_app()
    with app.app_context():  # 创建应用上下文
        # 确保数据库连接已初始化
        db.create_all()
        # 执行批量插入
        batch_insert_reports(1000)