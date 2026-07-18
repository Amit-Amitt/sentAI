"""Create IncidentMemory tables

Revision ID: 20260718_0002
Revises: 20260718_0001
Create Date: 2026-07-18 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260718_0002'
down_revision = '20260718_0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Incident Memories
    op.create_table('incident_memories',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        
        sa.Column('incident_id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', sa.UUID(as_uuid=True), nullable=False),
        
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('time_taken_ms', sa.Integer(), nullable=False),
        
        sa.Column('root_cause', sa.JSON(), nullable=False),
        sa.Column('recommended_fix', sa.JSON(), nullable=False),
        sa.Column('generated_report', sa.JSON(), nullable=False),
        sa.Column('timeline', sa.JSON(), nullable=False),
        
        sa.Column('logs_summary', sa.JSON(), nullable=False),
        sa.Column('metrics_summary', sa.JSON(), nullable=False),
        sa.Column('deployment_summary', sa.JSON(), nullable=False),
        
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_memories_incident_id'), 'incident_memories', ['incident_id'], unique=False)
    op.create_index(op.f('ix_incident_memories_workspace_id'), 'incident_memories', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_incident_memories_organization_id'), 'incident_memories', ['organization_id'], unique=False)
    op.create_index(op.f('ix_incident_memories_severity'), 'incident_memories', ['severity'], unique=False)

    # Incident Tags
    op.create_table('incident_tags',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('memory_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['memory_id'], ['incident_memories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_tags_memory_id'), 'incident_tags', ['memory_id'], unique=False)
    op.create_index(op.f('ix_incident_tags_name'), 'incident_tags', ['name'], unique=False)
    op.create_index(op.f('ix_incident_tags_value'), 'incident_tags', ['value'], unique=False)

    # Incident Embeddings
    op.create_table('incident_embeddings',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('memory_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('vector_reference', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['memory_id'], ['incident_memories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_embeddings_memory_id'), 'incident_embeddings', ['memory_id'], unique=True)


def downgrade() -> None:
    op.drop_table('incident_embeddings')
    op.drop_table('incident_tags')
    op.drop_table('incident_memories')
