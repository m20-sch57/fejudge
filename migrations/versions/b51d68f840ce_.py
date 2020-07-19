"""empty message

Revision ID: b51d68f840ce
Revises: ab982662b4b5
Create Date: 2020-07-19 19:54:34.370152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b51d68f840ce'
down_revision = 'ab982662b4b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('active_language')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active_language', sa.VARCHAR(length=16), nullable=True))

    # ### end Alembic commands ###
