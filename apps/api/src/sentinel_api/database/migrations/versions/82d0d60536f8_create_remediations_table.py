"""create_remediations_table

Revision ID: 82d0d60536f8
Revises: f22ae355b9df
Create Date: 2026-07-18 17:25:55.165408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82d0d60536f8'
down_revision: Union[str, None] = 'f22ae355b9df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('remediations',
        sa.Column('incident_id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('fix_strategy', sa.JSON(), nullable=True),
        sa.Column('code_patch', sa.JSON(), nullable=True),
        sa.Column('github_pr_draft', sa.JSON(), nullable=True),
        sa.Column('rollback_plan', sa.JSON(), nullable=True),
        sa.Column('risk_analysis', sa.JSON(), nullable=True),
        sa.Column('runbook', sa.JSON(), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_remediations_incident_id'), 'remediations', ['incident_id'], unique=False)
    op.create_index(op.f('ix_remediations_workspace_id'), 'remediations', ['workspace_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_remediations_workspace_id'), table_name='remediations')
    op.drop_index(op.f('ix_remediations_incident_id'), table_name='remediations')
    op.drop_table('remediations')
