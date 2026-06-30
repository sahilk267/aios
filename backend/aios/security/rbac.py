"""AIOS Role-Based Access Control (RBAC)."""

from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class Role(Enum):
    """System roles."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    AGENT = "agent"


class Permission(Enum):
    """System permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


# Role-permission mappings
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.EXECUTE, Permission.ADMIN},
    Role.DEVELOPER: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
    Role.VIEWER: {Permission.READ},
    Role.AGENT: {Permission.READ, Permission.WRITE, Permission.EXECUTE},
}


class RBACManager:
    """Manages role-based access control."""

    def __init__(self):
        self._user_roles: dict[str, Role] = {}
        self._logger = structlog.get_logger("aios.security.rbac")

    def assign_role(self, user_id: str, role: Role) -> None:
        """Assign a role to a user."""
        self._user_roles[user_id] = role
        self._logger.info("Role assigned", user_id=user_id, role=role.value)

    def get_role(self, user_id: str) -> Role:
        """Get user's role."""
        return self._user_roles.get(user_id, Role.VIEWER)

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a permission."""
        role = self.get_role(user_id)
        return permission in ROLE_PERMISSIONS.get(role, set())

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check permission and log result."""
        has = self.has_permission(user_id, permission)
        if not has:
            self._logger.warning(
                "Permission denied",
                user_id=user_id,
                permission=permission.value,
            )
        return has


# Global instance
rbac_manager = RBACManager()
