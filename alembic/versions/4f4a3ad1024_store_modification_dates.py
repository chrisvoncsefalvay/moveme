"""Store modification dates.

Revision ID: 4f4a3ad1024
Revises: 2d3585f9b6b5
Create Date: 2015-08-18 19:58:56.805239

"""

# revision identifiers, used by Alembic.
revision = '4f4a3ad1024'
down_revision = '2d3585f9b6b5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('boxes', sa.Column('last_modified', sa.String(63), nullable=True))
    op.add_column('items', sa.Column('last_modified', sa.String(63), nullable=True))


def downgrade():
    op.drop_column('boxes', 'last_modified')
    op.drop_column('items', 'last_modified')