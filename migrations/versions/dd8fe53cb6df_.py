"""empty message

Revision ID: dd8fe53cb6df
Revises: None
Create Date: 2016-07-28 13:42:04.404928

"""

# revision identifiers, used by Alembic.
revision = 'dd8fe53cb6df'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feed_setting_slack', sa.Column('user_data', sa.PickleType(), nullable=True))
    ### end Alembic commands ###
    # added by jwenerd
    # adjust this type to be a LONGBLOG
    op.execute('ALTER TABLE feed_setting_slack MODIFY user_data LONGBLOB')

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feed_setting_slack', 'user_data')
    ### end Alembic commands ###