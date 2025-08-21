from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any


class ReportUpdate(BaseModel):
    # 必填字段
    project_name: str = Field(..., min_length=1, description='项目名称')
    client_unit: str = Field(..., min_length=1, description='委托单位')
    inspection_object: str = Field(..., min_length=1, description='检验对象')
    inspection_type: str = Field(..., min_length=1, description='检验类型')
    inspection_conclusion: str = Field(..., min_length=1, description='检验结论')
    inspection_unit: str = Field(..., min_length=1, description='检验单位')
    
    # 可选字段 - 工程基本信息
    project_type: Optional[str] = Field(None, description='工程类型')
    project_location: Optional[str] = Field(None, description='工程地址')
    project_stage: Optional[str] = Field(None, description='工程阶段')
    construction_unit: Optional[str] = Field(None, description='建设单位')
    contractor: Optional[str] = Field(None, description='施工单位')
    supervisor: Optional[str] = Field(None, description='监理单位')
    witness_unit: Optional[str] = Field(None, description='见证单位')
    remarks: Optional[str] = Field(None, description='备注')

    # 可选字段 - 委托与受理信息
    client_contact: Optional[str] = Field(None, description='委托人')
    acceptance_date: Optional[date] = Field(None, description='受理日期')
    commission_date: Optional[date] = Field(None, description='委托日期')
    commission_code: Optional[str] = Field(None, description='委托编号')
    salesperson: Optional[str] = Field(None, description='业务员')

    # 可选字段 - 检测机构与资质
    certificate_no: Optional[str] = Field(None, description='资质证书编号')
    contact_address: Optional[str] = Field(None, description='联系地址')
    contact_phone: Optional[str] = Field(None, description='联系电话')

    # 可选字段 - 检测对象与参数
    object_part: Optional[str] = Field(None, description='检测部位')
    object_spec: Optional[str] = Field(None, description='对象规格')
    design_spec: Optional[str] = Field(None, description='设计要求')

    # 可选字段 - 检测项目与结果
    inspection_items: Optional[str] = Field(None, description='检测项目')
    test_items: Optional[str] = Field(None, description='检测项详情')
    inspection_quantity: Optional[int] = Field(None, ge=0, description='检测数量')
    measurement_unit: Optional[str] = Field(None, description='计量单位')
    conclusion_description: Optional[str] = Field(None, description='结论描述')
    is_recheck: Optional[bool] = Field(None, description='是否复检')

    # 可选字段 - 抽样与检测流程
    sampling_method: Optional[str] = Field(None, description='抽样方式')
    sampling_date: Optional[date] = Field(None, description='抽样日期')
    sampler: Optional[str] = Field(None, description='抽样人员')
    start_date: Optional[date] = Field(None, description='开始日期')
    end_date: Optional[date] = Field(None, description='结束日期')
    inspection_code: Optional[str] = Field(None, description='检测编号')
    inspector: Optional[str] = Field(None, description='检测员')
    tester_date: Optional[date] = Field(None, description='检测完成日期')

    # 可选字段 - 审批与归档
    reviewer: Optional[str] = Field(None, description='审核人')
    review_date: Optional[date] = Field(None, description='审核日期')
    approver: Optional[str] = Field(None, description='批准人')
    approve_date: Optional[date] = Field(None, description='批准日期')
    report_date: Optional[date] = Field(None, description='报告日期')
    issue_date: Optional[date] = Field(None, description='签发日期')

    # 可选字段 - 报告管理与附件
    report_status: Optional[str] = Field(None, description='报告状态')
    qrcode_content: Optional[str] = Field(None, description='二维码内容')
    attachment_paths: Optional[List[str]] = Field(None, description='附件路径')

class Config:
        from_attributes = True


class ReportUpdateResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None