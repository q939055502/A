from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import List, Optional


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='用户名')
    password: str = Field(..., min_length=3, max_length=20, description='密码')
    remember_me: Optional[bool] = Field(False, description='是否记住我')
    request_id: Optional[str] = Field(None, description='请求ID')


class StaffBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='用户名')
    email: EmailStr = Field(..., description='邮箱')
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    phone_number: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description='手机号')
    avatar: Optional[str] = Field(None, description='头像URL')
    gender: Optional[int] = Field(None, ge=0, le=2, description='性别(0:未知,1:男,2:女)')
    birthday: Optional[date] = Field(None, description='生日')
    address: Optional[str] = Field(None, max_length=200, description='地址')
    bio: Optional[str] = Field(None, max_length=500, description='个人简介')
    status: Optional[int] = Field(1, ge=1, le=2, description='状态(1:启用,1:禁用)')


class StaffCreate(StaffBase):
    password: str = Field(..., min_length=6, max_length=20, description='密码')
    role_ids: Optional[List[int]] = Field(None, description='角色ID列表')

    @field_validator('password')
    def validate_password(cls, v):
        if not v[0].isalpha():
            raise ValueError('密码必须以字母开头')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class StaffUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description='用户名')
    email: Optional[EmailStr] = Field(None, description='邮箱')
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    phone_number: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description='手机号')
    avatar: Optional[str] = Field(None, description='头像URL')
    gender: Optional[int] = Field(None, ge=0, le=2, description='性别(0:未知,1:男,2:女)')
    birthday: Optional[date] = Field(None, description='生日')
    address: Optional[str] = Field(None, max_length=200, description='地址')
    bio: Optional[str] = Field(None, max_length=500, description='个人简介')
    status: Optional[int] = Field(None, ge=0, le=1, description='状态(0:禁用,1:启用)')
    password: Optional[str] = Field(None, min_length=6, max_length=20, description='密码')
    id_card_number: Optional[str] = Field(None, pattern=r'^\d{17}[\dXx]$', description='身份证号')

    @field_validator('password')
    def validate_password(cls, v):
        if v is None:
            return v
        if not v[0].isalpha():
            raise ValueError('密码必须以字母开头')
        if not any(char.isalpha() for char in v):
            raise ValueError('密码必须包含至少一个字母')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class StaffRoleUpdate(BaseModel):
    role_ids: List[int] = Field(..., description='角色ID列表')


class StaffPermissionUpdate(BaseModel):
    permission_ids: List[int] = Field(..., description='权限ID列表')


# 响应模型
class StaffResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    phone_number: Optional[str]
    avatar: Optional[str]
    gender: Optional[int]
    birthday: Optional[date]
    address: Optional[str]
    bio: Optional[str]
    status: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class PaginatedStaffResponse(BaseModel):
    items: List[StaffResponse]
    total: int
    page: int
    per_page: int