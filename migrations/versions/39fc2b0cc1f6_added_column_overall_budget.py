"""added column overall_budget

Revision ID: 39fc2b0cc1f6
Revises: 47753e11121b
Create Date: 2024-07-13 18:19:55.460140

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39fc2b0cc1f6'
down_revision = '47753e11121b'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('sponsor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('overall_budget', sa.Float(), nullable=False, server_default='0.0'))
    # After adding the column, drop the server_default
    op.alter_column('sponsor', 'overall_budget', server_default=None)

def downgrade():
    with op.batch_alter_table('sponsor', schema=None) as batch_op:
        batch_op.drop_column('overall_budget')