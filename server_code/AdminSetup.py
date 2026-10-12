"""Trusted setup process for roles.

Nothing here is decorated with @anvil.server.callable, so the browser
can NEVER call these functions. Run them from the Anvil Server Console
(or edit the 'role' cell directly in the Data Tables editor).

Example (Server Console):
    import AdminSetup
    AdminSetup.make_admin("teacher@example.com")
"""
from anvil.tables import app_tables

ALLOWED_ROLES = ["Student", "Admin"]


def set_user_role(email, role):
    if role not in ALLOWED_ROLES:
        raise ValueError("Role must be one of: " + ", ".join(ALLOWED_ROLES))
    user = app_tables.users.get(email=email)
    if user is None:
        raise ValueError("No user with email " + email)
    user["role"] = role
    return "{} is now {}".format(email, role)


def make_admin(email):
    return set_user_role(email, "Admin")


def make_student(email):
    return set_user_role(email, "Student")
