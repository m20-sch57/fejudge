"""empty message

Revision ID: ab982662b4b5
Revises: 887d91731810
Create Date: 2020-07-18 17:32:26.605167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab982662b4b5'
down_revision = '887d91731810'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('protocol', sa.Text(), nullable=True))
        batch_op.drop_column('details')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('details', sa.TEXT(), nullable=True))
        batch_op.drop_column('protocol')

    # ### end Alembic commands ###