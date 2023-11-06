"""empty message

Revision ID: 457cb6a71a1c
Revises: d910b924071c
Create Date: 2023-11-05 08:31:23.892012

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '457cb6a71a1c'
down_revision = 'd910b924071c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=50),
               type_=sa.Enum('admin', 'user'),
               nullable=True)
        batch_op.drop_index('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('roles', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=False)
        batch_op.alter_column('name',
               existing_type=sa.Enum('admin', 'user'),
               type_=mysql.VARCHAR(length=50),
               nullable=False)

    # ### end Alembic commands ###
