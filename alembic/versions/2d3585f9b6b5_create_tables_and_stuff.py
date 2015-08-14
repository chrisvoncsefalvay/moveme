"""Create tables and stuff

Revision ID: 2d3585f9b6b5
Revises: 
Create Date: 2015-08-12 12:21:01.603759

"""

# revision identifiers, used by Alembic.
revision = '2d3585f9b6b5'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('boxes',
                    sa.Column('internal_id', sa.Integer, primary_key=True),
                    sa.Column('box_uuid', sa.String(63), nullable=False),
                    sa.Column('description', sa.String(255)),
                    sa.Column('location', sa.String(63)))
    op.create_table('items',
                    sa.Column('internal_id', sa.Integer, primary_key=True),
                    sa.Column('item_uuid', sa.String(63), nullable=False),
                    sa.Column('description', sa.String(255)),
                    sa.Column('in_box', sa.String(63)))

def downgrade():
    op.drop_table('boxes')
    op.drop_table('items')
