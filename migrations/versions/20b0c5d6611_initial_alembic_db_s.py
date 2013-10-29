"""initial alembic db setup

Revision ID: 20b0c5d6611
Revises: None
Create Date: 2013-10-29 19:29:10.256789

"""

# revision identifiers, used by Alembic.
revision = '20b0c5d6611'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('files',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('owner_hash', sa.String(40), default="", nullable=False, unique=True),
        sa.Column('access_hash', sa.String(40), default="", nullable=False),
        sa.Column('content', sa.Text, default="", nullable=False),
    )

def downgrade():
    op.drop_table('files')
    pass
