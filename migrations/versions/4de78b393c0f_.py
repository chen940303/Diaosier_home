"""empty message

Revision ID: 4de78b393c0f
Revises: None
Create Date: 2016-05-01 17:38:42.017638

"""

# revision identifiers, used by Alembic.
revision = '4de78b393c0f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###
