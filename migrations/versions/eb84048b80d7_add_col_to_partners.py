"""add col to partners

Revision ID: eb84048b80d7
Revises: 
Create Date: 2023-07-09 09:09:51.653709

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb84048b80d7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('partnersignup', sa.Column('dri_rate', sa.Integer(), nullable=True))
    op.add_column('site_visits', sa.Column('add_col', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('site_visits', 'add_col')
    op.drop_column('partnersignup', 'dri_rate')
    # ### end Alembic commands ###