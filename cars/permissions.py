def user_is_admin(user) -> bool:
    """Staff/superuser or Role.code == ADMIN."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    role = getattr(user, "role", None)
    return role is not None and getattr(role, "code", None) == "ADMIN"


def user_is_mechanic(user) -> bool:
    """Role.code == MECHANIC (used for maintenance record write access)."""
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, "role", None)
    return role is not None and getattr(role, "code", None) == "MECHANIC"


def user_is_owner(user) -> bool:
    """Role.code == OWNER (car owner; read-only on maintenance records)."""
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, "role", None)
    return role is not None and getattr(role, "code", None) == "OWNER"
