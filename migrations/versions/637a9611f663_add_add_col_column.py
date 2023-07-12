"""Add add_col column

Revision ID: 637a9611f663
Revises: eb84048b80d7
Create Date: 2023-07-09 09:30:52.150680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '637a9611f663'
down_revision = 'eb84048b80d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('partnersignup', 'dri_rate')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('partnersignup', sa.Column('dri_rate', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###