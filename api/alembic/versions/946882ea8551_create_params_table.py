"""create params table

Revision ID: 946882ea8551
Revises: 
Create Date: 2020-08-26 13:18:07.654073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '946882ea8551'
down_revision = None
branch_labels = None
depends_on = None

"""
    the `params` table tracks the params calculated from each trackout
    before processing is applied.

    track_id is the id of the Track.
    trackout_id is the id of the Trackout that this was generated from.
    kind is whether it was generated from compression, eq, deesser, etc...
    data is a JSON object of the params that were generated.
"""


def upgrade():
    op.create_table(
        'params',
        sa.Column('track_id', sa.String),
        sa.Column('trackout_id', sa.String),
        sa.Column('kind', sa.String),
        sa.Column('data', sa.JSON)
    )
    pass


def downgrade():
    op.drop_table('params')
    pass
