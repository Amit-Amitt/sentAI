import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.role import Permission, Role

logger = structlog.get_logger("sentinel_api.database.seed")


async def seed_roles_and_permissions(session: AsyncSession) -> None:
    """Seeds default Roles and Permissions in the database on startup."""
    logger.info("Seeding roles and permissions...")

    # 1. Define all permissions
    permissions_data = {
        "full_access": "Full access to all settings, billing, members, and data.",
        "manage_members": "Invite, update roles, and remove team members.",
        "manage_workspace": "Configure and update workspace preferences.",
        "run_incidents": "Trigger, mitigate, and resolve AI incident responses.",
        "view_reports": "Access post-mortem investigations and reports.",
        "manage_ai_configs": "Modify active SRE agent model prompts and strategies.",
    }

    # Query existing permissions
    existing_perms_res = await session.execute(select(Permission))
    existing_perms_map = {p.name: p for p in existing_perms_res.scalars().all()}

    # Create missing permissions
    for name, desc in permissions_data.items():
        if name not in existing_perms_map:
            p = Permission(name=name, description=desc)
            session.add(p)
            existing_perms_map[name] = p

    # Flush to ensure permissions have IDs generated
    await session.flush()

    # 2. Define all roles with their assigned permissions
    roles_data = {
        "owner": {
            "desc": "Owner of the organization with full transfer/billing permissions.",
            "perms": [
                "full_access",
                "manage_members",
                "manage_workspace",
                "run_incidents",
                "view_reports",
                "manage_ai_configs",
            ],
        },
        "admin": {
            "desc": "Organization administrator with member and workspace management rights.",
            "perms": [
                "manage_members",
                "manage_workspace",
                "run_incidents",
                "view_reports",
                "manage_ai_configs",
            ],
        },
        "engineer": {
            "desc": "SRE Engineer capable of running incidents and viewing reports.",
            "perms": ["run_incidents", "view_reports", "manage_ai_configs"],
        },
        "viewer": {
            "desc": "Read-only access to dashboard data and incident reports.",
            "perms": ["view_reports"],
        },
    }

    # Query existing roles
    existing_roles_res = await session.execute(select(Role))
    existing_roles_map = {r.name: r for r in existing_roles_res.scalars().all()}

    # Create/update roles with relationships
    for name, info in roles_data.items():
        role = existing_roles_map.get(name)
        if not role:
            role = Role(name=name, description=info["desc"])
            session.add(role)
        role.permissions = [existing_perms_map[pname] for pname in info["perms"]]

    await session.commit()
    logger.info("Roles and permissions seeding completed.")
