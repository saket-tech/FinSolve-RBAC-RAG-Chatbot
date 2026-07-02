"""Role-based access control definitions."""

from enum import Enum


class Role(str, Enum):
    FINANCE = "finance"
    MARKETING = "marketing"
    HR = "hr"
    ENGINEERING = "engineering"
    EXECUTIVE = "executive"
    EMPLOYEE = "employee"


# Maps each role to allowed document departments (folder names under data/)
ROLE_DEPARTMENT_ACCESS: dict[Role, set[str]] = {
    Role.FINANCE: {"finance"},
    Role.MARKETING: {"marketing"},
    Role.HR: {"hr", "general"},
    Role.ENGINEERING: {"engineering"},
    Role.EXECUTIVE: {"finance", "marketing", "hr", "engineering", "general"},
    Role.EMPLOYEE: {"general"},
}


def get_allowed_departments(role: Role) -> list[str]:
    """Return sorted list of departments the role may access."""
    return sorted(ROLE_DEPARTMENT_ACCESS.get(role, set()))


def can_access_department(role: Role, department: str) -> bool:
    """Check if a role may access a given department."""
    return department in ROLE_DEPARTMENT_ACCESS.get(role, set())
