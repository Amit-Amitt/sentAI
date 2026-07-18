"""Create integrations marketplace tables.

Revision ID: 20260718_0002
Revises: 20260718_0001
Create Date: 2026-07-18 14:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260718_0003"
down_revision = "20260718_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create integration_providers
    op.create_table(
        "integration_providers",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("logo", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("overview", sa.String(length=5000), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="available"),
        sa.Column("is_oauth_supported", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("default_sync_frequency", sa.String(length=50), nullable=False, server_default="daily"),
        sa.UniqueConstraint("key", name="uq_integration_providers_key"),
    )
    op.create_index("ix_integration_providers_key", "integration_providers", ["key"])

    # 2. Create workspace_integrations
    op.create_table(
        "workspace_integrations",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("provider_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="disconnected"),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["integration_providers.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_workspace_integrations_workspace_id", "workspace_integrations", ["workspace_id"])
    op.create_index("ix_workspace_integrations_provider_id", "workspace_integrations", ["provider_id"])

    # 3. Create integration_credentials
    op.create_table(
        "integration_credentials",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_integration_id", sa.String(length=36), nullable=False),
        sa.Column("credential_type", sa.String(length=50), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=1000), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workspace_integration_id"], ["workspace_integrations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_integration_credentials_conn_id", "integration_credentials", ["workspace_integration_id"])

    # 4. Create integration_webhooks
    op.create_table(
        "integration_webhooks",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_integration_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False, server_default="incoming"),
        sa.Column("secret", sa.String(length=255), nullable=True),
        sa.Column("retry_strategy", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("delivery_status", sa.String(length=50), nullable=True),
        sa.Column("delivery_history", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_integration_id"], ["workspace_integrations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_integration_webhooks_conn_id", "integration_webhooks", ["workspace_integration_id"])

    # 5. Create integration_syncs
    op.create_table(
        "integration_syncs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_integration_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="success"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_resources", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_integration_id"], ["workspace_integrations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_integration_syncs_conn_id", "integration_syncs", ["workspace_integration_id"])

    # 6. Create integration_audits
    op.create_table(
        "integration_audits",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("workspace_integration_id", sa.String(length=36), nullable=True),
        sa.Column("workspace_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("performed_by_id", sa.String(length=36), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_integration_id"], ["workspace_integrations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_integration_audits_conn_id", "integration_audits", ["workspace_integration_id"])
    op.create_index("ix_integration_audits_workspace_id", "integration_audits", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_integration_audits_workspace_id", table_name="integration_audits")
    op.drop_index("ix_integration_audits_conn_id", table_name="integration_audits")
    op.drop_table("integration_audits")

    op.drop_index("ix_integration_syncs_conn_id", table_name="integration_syncs")
    op.drop_table("integration_syncs")

    op.drop_index("ix_integration_webhooks_conn_id", table_name="integration_webhooks")
    op.drop_table("integration_webhooks")

    op.drop_index("ix_integration_credentials_conn_id", table_name="integration_credentials")
    op.drop_table("integration_credentials")

    op.drop_index("ix_workspace_integrations_provider_id", table_name="workspace_integrations")
    op.drop_index("ix_workspace_integrations_workspace_id", table_name="workspace_integrations")
    op.drop_table("workspace_integrations")

    op.drop_index("ix_integration_providers_key", table_name="integration_providers")
    op.drop_table("integration_providers")
