"""Add bio column to user table

Revision ID: 02bef89540f7
Revises: 6c6fcf9133ce
Create Date: 2025-06-06 01:16:15.183844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02bef89540f7'
down_revision = '6c6fcf9133ce'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users_persistence', sa.Column('bio', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users_persistence', 'bio')
    # ### end Alembic commands ###
