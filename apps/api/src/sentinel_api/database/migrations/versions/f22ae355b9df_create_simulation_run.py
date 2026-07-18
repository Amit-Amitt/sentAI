"""create_simulation_run

Revision ID: f22ae355b9df
Revises: 20260718_0003
Create Date: 2026-07-18 17:05:36.181897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f22ae355b9df'
down_revision: Union[str, None] = '20260718_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('simulation_runs',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('scenario_id', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RUNNING'),
        sa.Column('incident_id', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulation_runs_workspace_id'), 'simulation_runs', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_simulation_runs_incident_id'), 'simulation_runs', ['incident_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_simulation_runs_incident_id'), table_name='simulation_runs')
    op.drop_index(op.f('ix_simulation_runs_workspace_id'), table_name='simulation_runs')
    op.drop_table('simulation_runs')
