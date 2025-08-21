"""'Fix database migration issues'

Revision ID: 5bbb78b040da
Revises: 487cbbeca383
Create Date: 2025-08-21 00:09:46.832128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bbb78b040da'
down_revision = '487cbbeca383'
branch_labels = None
depends_on = None


def upgrade():
    # 确保inspection_reports表中的registrant字段是可空的
    with op.batch_alter_table('inspection_reports', schema=None) as batch_op:
        batch_op.alter_column('registrant', existing_type=sa.String(length=255), nullable=True)


def downgrade():
    # 恢复inspection_reports表中的registrant字段为必填
    with op.batch_alter_table('inspection_reports', schema=None) as batch_op:
        batch_op.alter_column('registrant', existing_type=sa.String(length=255), nullable=False)
