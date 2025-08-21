"""Add last_modified_by field and make registrant required

Revision ID: fdafcc58b834
Revises: 3d646381c488
Create Date: 2025-08-17 21:40:43.301718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdafcc58b834'
down_revision = '3d646381c488'
branch_labels = None
depends_on = None


def upgrade():
    # 添加last_modified_by字段（移除注释，因为SQLite不支持）
    op.add_column('inspection_reports', sa.Column('last_modified_by', sa.String(length=50), nullable=True))

    # 先更新现有数据中的NULL值
    op.execute('UPDATE inspection_reports SET registrant = \'admin\' WHERE registrant IS NULL')

    # 修改registrant字段为必填
    op.alter_column('inspection_reports', 'registrant',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)


def downgrade():
    # 删除last_modified_by字段
    op.drop_column('inspection_reports', 'last_modified_by')

    # 恢复registrant字段为可选
    op.alter_column('inspection_reports', 'registrant',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
