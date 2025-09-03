from app.db import db
from datetime import datetime, timezone
from app.utils.user_utils import get_user_nickname


class InspectionReport(db.Model):
    """检测报告数据库模型"""
    __tablename__ = 'inspection_reports'

    # 一、工程基本信息
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 检测报告的唯一标识，自增主键
    project_name = db.Column(db.String(200), nullable=False, comment='工程名称')  # 检测对应的工程整体名称
    project_location = db.Column(db.String(200), comment='工程地址')  # 工程具体地址，用于定位项目现场
    project_type = db.Column(db.String(50), comment='工程类型')  # 工程类别（如建筑工程、市政桥梁）
    project_stage = db.Column(db.String(50), comment='工程阶段')  # 工程当前阶段（如地基基础、主体结构）
    construction_unit = db.Column(db.String(100), comment='建设单位')  # 工程的建设单位名称
    contractor = db.Column(db.String(100), comment='施工单位')  # 工程的施工单位名称
    supervisor = db.Column(db.String(100), comment='监理单位')  # 工程的监理单位名称
    witness_unit = db.Column(db.String(100), comment='见证单位')  # 见证检测过程的单位名称
    remarks = db.Column(db.Text, comment='备注')  # 关于检测的补充说明信息

    # 二、委托与受理信息
    client_unit = db.Column(db.String(200), nullable=False, comment='委托单位')  # 委托检测的单位名称
    client_contact = db.Column(db.String(50), comment='委托人')  # 委托单位的联系人姓名
    acceptance_date = db.Column(db.Date, comment='受理日期')  # 检测机构受理该检测委托的日期
    commission_date = db.Column(db.Date,nullable=True, comment='委托日期')  # 委托单位提交检测委托的日期
    commission_code = db.Column(db.String(100), comment='委托编号')  # 检测委托的编号
    salesperson = db.Column(db.String(50),  default="default_sales", comment='业务员')  # 对接该检测业务的销售人员姓名

    # 三、检测机构与资质
    inspection_unit = db.Column(db.String(200),  comment='检测单位')  # 执行检测的机构名称
    certificate_no = db.Column(db.String(50), comment='资质证书编号')  # 检测机构的资质证书编号
    contact_address = db.Column(db.String(200), comment='联系地址')  # 检测单位的联系地址
    contact_phone = db.Column(db.String(50), comment='联系电话')  # 检测单位的联系电话

    # 四、检测对象与参数
    inspection_object = db.Column(db.String(100), nullable=True, comment='检测对象')  # 被检测的具体对象名称
    object_part = db.Column(db.String(100), comment='检测部位')  # 具体检测的部位
    object_spec = db.Column(db.String(100), comment='对象规格')  # 检测对象的规格参数
    design_spec = db.Column(db.Text, comment='设计要求')  # 检测对象的设计标准参数
    inspection_type = db.Column(db.String(50),  comment='检验类型')  # 检测的类型分类

    # 五、检测项目与结果
    inspection_items = db.Column(db.String(200), comment='检测项目')  # 本次检测包含的具体项目
    test_items = db.Column(db.String(500), comment='检测项详情')  # 字符串存储各检测项的标准、结果和单项结论
    inspection_quantity = db.Column(db.Integer, comment='检测数量')  # 本次检测的样本数量
    measurement_unit = db.Column(db.String(20), comment='计量单位')  # 检测数量的计量单位
    inspection_conclusion = db.Column(db.String(200), nullable=True, comment='检测结果')  # 合格/不合格/异常
    conclusion_description = db.Column(db.Text, comment='结论描述')  # 对检测结果的详细说明
    is_recheck = db.Column(db.Boolean, default=False, comment='是否复检')  # 标记该报告是否为复检结果

    # 六、抽样与检测流程
    sampling_method = db.Column(db.String(50), comment='抽样方式')  # 样本采集的方式
    sampling_date = db.Column(db.Date, comment='抽样日期')  # 样本采集的日期
    sampler = db.Column(db.String(50), comment='抽样人员')  # 执行抽样的人员姓名
    start_date = db.Column(db.Date, comment='开始日期')  # 检测工作实际开始的日期
    end_date = db.Column(db.Date, comment='结束日期')  # 检测工作实际完成的日期
    inspection_code = db.Column(db.String(50), comment='检测编号')  # 检测流程的内部编号
    inspector = db.Column(db.String(50), comment='检测员')  # 执行检测工作的人员姓名
    tester_date = db.Column(db.Date, comment='检测完成日期')  # 检测员完成检测工作并提交结果的日期

    # 七、审批与归档
    reviewer = db.Column(db.String(50), comment='审核人')  # 审核检测报告的人员姓名
    review_date = db.Column(db.Date, comment='审核日期')  # 审核人完成报告审核的日期
    approver = db.Column(db.String(50), comment='批准人')  # 批准报告生效的人员姓名
    approve_date = db.Column(db.Date, comment='批准日期')  # 批准人完成报告批准的日期
    report_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date(), comment='报告日期')  # 报告生成的日期
    issue_date = db.Column(db.Date, comment='签发日期')  # 报告正式签发的日期

    # 八、报告管理与附件
    report_code = db.Column(db.String(100), nullable=False, unique=True, comment='报告编号')  # 报告的唯一编号
    report_status = db.Column(db.String(20), nullable=True, default='草稿', comment='报告状态')  # 报告当前的处理状态
    qrcode_content = db.Column(db.String(200), comment='二维码内容')  # 报告对应的二维码信息
    attachment_paths = db.Column(db.JSON, comment='附件路径')  # 检测原始记录、现场照片等附件的存储路径

    # 九、通用管理字段
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 报告记录创建的时间
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # 报告记录最后修改的时间

    registrant_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='登记人ID')  # 登记人ID，外键关联users表
    registrant = db.Column(db.String(50), comment='登记人')  # 登记人昵称或者账号

    
    last_modified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='最后修改人ID')  # 最后修改该报告的人员ID，外键关联users表
    last_modified_by = db.Column(db.String(50), comment='最后修改人')  # 最后修改该报告的人员姓名


    def __repr__(self):
        return f'<InspectionReport {self.report_code} (ID: {self.id})>'

    def to_dict(self):
        """将模型转换为字典格式
        返回的字典包含检测报告的所有关键信息，方便API返回或数据处理
        """
        
        return {
            'id': self.id,  # 报告ID
            'project_name': self.project_name,  # 项目名称
            'project_location': self.project_location,  # 项目地点
            'project_type': self.project_type,  # 项目类型
            'project_stage': self.project_stage,  # 项目阶段
            'construction_unit': self.construction_unit,  # 建设单位
            'contractor': self.contractor,  # 施工单位
            'supervisor': self.supervisor,  # 监理单位
            'witness_unit': self.witness_unit,  # 见证单位
            'remarks': self.remarks,  # 备注信息
            'client_unit': self.client_unit,  # 委托单位
            'client_contact': self.client_contact,  # 委托单位联系人
            'acceptance_date': datetime.combine(self.acceptance_date, datetime.min.time()).strftime('%Y-%m-%d') if self.acceptance_date else None,  # 受理日期
            'commission_date': datetime.combine(self.commission_date, datetime.min.time()).strftime('%Y-%m-%d') if self.commission_date else None,  # 委托日期
            'commission_code': self.commission_code,  # 委托编号
            'salesperson': self.salesperson,  # 业务员
            'inspection_unit': self.inspection_unit,  # 检测单位
            'certificate_no': self.certificate_no,  # 资质证书编号
            'contact_address': self.contact_address,  # 联系地址
            'contact_phone': self.contact_phone,  # 联系电话
            'contact_phone': self.contact_phone,  # 联系电话
            'registrant': get_user_nickname(self.registrant_id) if self.registrant_id else '',  # 登记人、创建人
            'registrant_id': self.registrant_id,  # 登记人ID

            'inspection_object': self.inspection_object,  # 检测对象
            'object_part': self.object_part,  # 对象部位
            'object_spec': self.object_spec,  # 对象规格
            'design_spec': self.design_spec,  # 设计要求
            'inspection_type': self.inspection_type,  # 检验类型
            'inspection_items': self.inspection_items,  # 检测项目
            'test_items': self.test_items,  # 试验项目
            'inspection_quantity': self.inspection_quantity,  # 检测数量
            'measurement_unit': self.measurement_unit,  # 计量单位
            'inspection_conclusion': self.inspection_conclusion,  # 检测结果 (合格/不合格/异常。。。)
            'conclusion_description': self.conclusion_description,  # 结论描述
            'is_recheck': self.is_recheck,  # 是否为复检
            'sampling_method': self.sampling_method,  # 抽样方法
            'sampling_date': datetime.combine(self.sampling_date, datetime.min.time()).strftime('%Y-%m-%d') if self.sampling_date else None,  # 抽样日期
            'sampler': self.sampler,  # 抽样人
            'start_date': datetime.combine(self.start_date, datetime.min.time()).strftime('%Y-%m-%d') if self.start_date else None,  # 开始日期
            'end_date': datetime.combine(self.end_date, datetime.min.time()).strftime('%Y-%m-%d') if self.end_date else None,  # 结束日期
            'inspection_code': self.inspection_code,  # 检测编号
            'inspector': self.inspector,  # 检测人
            'tester_date': datetime.combine(self.tester_date, datetime.min.time()).strftime('%Y-%m-%d') if self.tester_date else None,  # 检测日期
            'reviewer': self.reviewer,  # 审核人
            'review_date': datetime.combine(self.review_date, datetime.min.time()).strftime('%Y-%m-%d') if self.review_date else None,  # 审核日期
            'approver': self.approver,  # 批准人
            'approve_date': datetime.combine(self.approve_date, datetime.min.time()).strftime('%Y-%m-%d') if self.approve_date else None,  # 批准日期
            'report_date': datetime.combine(self.report_date, datetime.min.time()).strftime('%Y-%m-%d') if self.report_date else None,  # 报告日期
            'issue_date': datetime.combine(self.issue_date, datetime.min.time()).strftime('%Y-%m-%d') if self.issue_date else None,  # 发放日期
            'report_code': self.report_code,  # 报告编号
            'report_status': self.report_status,  # 报告状态
            'qrcode_content': self.qrcode_content,  # 二维码内容
            'attachment_paths': self.attachment_paths,  # 附件路径
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,  # 创建时间
            'last_modified_by': get_user_nickname(self.last_modified_by_id) if self.last_modified_by_id else '',  # 最后修改人
            'last_modified_by_id': self.last_modified_by_id,  # 最后修改人ID


            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,  # 更新时间
            'is_deleted': self.is_deleted  # 是否删除
        }

    
    def to_dict_cn(self):
        """将模型转换为中文键的字典格式"""
        data = self.to_dict()
        field_mapping = self.get_field_mapping()
        return {field_mapping.get(key, key): value for key, value in data.items()}

    @classmethod
    def get_field_mapping(cls):
        """获取字段名到中文的映射字典"""
        return {
            'id': 'ID',
            'project_name': '工程名称',
            'project_location': '工程地址',
            'project_type': '工程类型',
            'project_stage': '工程阶段',
            'construction_unit': '建设单位',
            'contractor': '施工单位',
            'supervisor': '监理单位',
            'witness_unit': '见证单位',
            'remarks': '备注',
            'client_unit': '委托单位',
            'client_contact': '委托人',
            'acceptance_date': '受理日期',
            'commission_date': '委托日期',
            'commission_code': '委托编号',
            'salesperson': '业务员',
            'inspection_unit': '检测单位',
            'certificate_no': '资质证书编号',
            'contact_address': '联系地址',
            'contact_phone': '联系电话',
            'registrant': '登记人',
            'inspection_object': '检测对象',
            'object_part': '检测部位',
            'object_spec': '对象规格',
            'design_spec': '设计要求',
            'inspection_type': '检验类型',
            'inspection_items': '检测项目',
            'test_items': '检测项详情',
            'inspection_quantity': '检测数量',
            'measurement_unit': '计量单位',
            'inspection_conclusion': '检测结果',
            'conclusion_description': '结论描述',
            'is_recheck': '是否复检',
            'sampling_method': '抽样方式',
            'sampling_date': '抽样日期',
            'sampler': '抽样人员',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'inspection_code': '检测编号',
            'inspector': '检测员',
            'tester_date': '检测完成日期',
            'reviewer': '审核人',
            'review_date': '审核日期',
            'approver': '批准人',
            'approve_date': '批准日期',
            'report_date': '报告日期',
            'issue_date': '签发日期',
            'report_code': '报告编号',
            'report_status': '报告状态',
            'qrcode_content': '二维码内容',
            'attachment_paths': '附件路径',
            'created_at': '创建时间',
            'updated_at': '更新时间',
            'is_deleted': '软删除标记'
        }