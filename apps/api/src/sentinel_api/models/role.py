import uuid
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import Base, BaseModel

# Association table for Role <-> Permission many-to-many
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(BaseModel):
    """Granular system permissions for role-based access control."""

    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Role(BaseModel):
    """System roles containing a set of permissions."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    permissions = relationship(
        "Permission", secondary=role_permissions, lazy="selectin"
    )
