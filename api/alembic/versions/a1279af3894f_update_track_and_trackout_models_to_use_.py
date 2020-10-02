"""update track and trackout models to use uuids

Revision ID: a1279af3894f
Revises: 946882ea8551
Create Date: 2020-10-02 15:30:12.059250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1279af3894f'
down_revision = '946882ea8551'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('track', sa.Column('uuid', sa.String()))
    op.add_column('track_out', sa.Column('uuid', sa.String()))
    pass


def downgrade():
    op.drop_column('track', 'uuid')
    op.drop_column('track_out', 'uuid')
    pass
