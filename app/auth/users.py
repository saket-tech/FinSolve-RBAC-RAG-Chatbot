"""Demo user accounts for authentication."""

from app.auth.rbac import Role

# Demo credentials for evaluation and testing.
# Password for all demo users: finsolve123
DEMO_USERS: dict[str, dict] = {
    "finance_user": {
        "password": "finsolve123",
        "role": Role.FINANCE,
        "display_name": "Finance Team Member",
    },
    "marketing_user": {
        "password": "finsolve123",
        "role": Role.MARKETING,
        "display_name": "Marketing Team Member",
    },
    "hr_user": {
        "password": "finsolve123",
        "role": Role.HR,
        "display_name": "HR Team Member",
    },
    "engineering_user": {
        "password": "finsolve123",
        "role": Role.ENGINEERING,
        "display_name": "Engineering Team Member",
    },
    "executive_user": {
        "password": "finsolve123",
        "role": Role.EXECUTIVE,
        "display_name": "C-Level Executive",
    },
    "employee_user": {
        "password": "finsolve123",
        "role": Role.EMPLOYEE,
        "display_name": "General Employee",
    },
}


def authenticate_user(username: str, password: str) -> dict | None:
    """Validate credentials and return user info if valid."""
    user = DEMO_USERS.get(username)
    if user and user["password"] == password:
        return {
            "username": username,
            "role": user["role"],
            "display_name": user["display_name"],
        }
    return None
