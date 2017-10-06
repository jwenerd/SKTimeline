"""empty message

Revision ID: 8d02f9fa2576
Revises: 11d36c57880d
Create Date: 2017-10-06 16:09:59.638866

"""

# revision identifiers, used by Alembic.
revision = '8d02f9fa2576'
down_revision = '11d36c57880d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('github_feed_items', sa.Column('feed_user_id', sa.BigInteger, sa.ForeignKey("feed_item_users.id"),  nullable=True))
    op.add_column('slack_feed_items', sa.Column('feed_user_id', sa.BigInteger,  sa.ForeignKey("feed_item_users.id"),  nullable=True))
    op.add_column('twitter_feed_items', sa.Column('feed_user_id', sa.BigInteger, sa.ForeignKey("feed_item_users.id"), nullable=True))

def downgrade():
    op.drop_column('github_feed_items', 'feed_user_id')
    op.drop_column('slack_feed_items', 'feed_user_id')
    op.drop_column('twitter_feed_items', 'feed_user_id')
