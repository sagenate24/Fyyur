"""empty message

Revision ID: f8ab52be12f8
Revises: 48d172380a24
Create Date: 2019-11-22 16:58:13.143776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ab52be12f8'
down_revision = '48d172380a24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###