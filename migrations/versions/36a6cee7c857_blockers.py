"""blockers

Revision ID: 36a6cee7c857
Revises: 68d3f8e39421
Create Date: 2021-04-30 02:03:27.024773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36a6cee7c857'
down_revision = '68d3f8e39421'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blockers',
    sa.Column('blocker_id', sa.Integer(), nullable=True),
    sa.Column('blocked_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blocked_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['blocker_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blockers')
    # ### end Alembic commands ###
