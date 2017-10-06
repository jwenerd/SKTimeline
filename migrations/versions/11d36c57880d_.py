"""empty message

Revision ID: 11d36c57880d
Revises: dd8fe53cb6df
Create Date: 2017-10-06 16:08:10.017398

"""

# revision identifiers, used by Alembic.
revision = '11d36c57880d'
down_revision = 'dd8fe53cb6df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'users', ['username'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    ### end Alembic commands ###
