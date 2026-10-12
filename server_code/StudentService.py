import anvil.server
import anvil.users
from anvil.tables import app_tables

VALID_COURSES = ["BSIT", "BSCS", "BSIS"]
VALID_YEARS = [1, 2, 3, 4]


def require_admin():
    user = anvil.users.get_user()

    if user is None:
        raise PermissionError("Please log in first.")

    if user["role"] != "Admin":
        raise PermissionError(
            "Administrator access required."
        )

    return user


@anvil.server.callable(require_user=True)
def register_student(student_id, name, course, year):
    student_id = (student_id or "").strip()
    name = (name or "").strip()
    course = (course or "").strip()

    if not student_id:
        raise ValueError("Student ID is required.")

    if not name:
        raise ValueError("Student name is required.")

    if course not in VALID_COURSES:
        raise ValueError("Invalid course.")

    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ValueError("Year level must be a number.")

    if year not in VALID_YEARS:
        raise ValueError("Invalid year level.")

    existing = app_tables.students.get(
        student_id=student_id
    )

    if existing is not None:
        raise ValueError("Student ID already exists.")

    user = anvil.users.get_user()

    app_tables.students.add_row(
        student_id=student_id,
        name=name,
        course=course,
        year_level=year,
        owner=user
    )

    return "Registration successful."


@anvil.server.callable(require_user=True)
def get_my_registrations():
    user = anvil.users.get_user()
    records = app_tables.students.search(owner=user)

    return [
        {
            "student_id": row["student_id"],
            "name": row["name"],
            "course": row["course"],
            "year_level": row["year_level"]
        }
        for row in records
    ]


@anvil.server.callable(require_user=True)
def get_all_registrations():
    require_admin()
    records = app_tables.students.search()

    return [
        {
            "student_id": row["student_id"],
            "name": row["name"],
            "course": row["course"],
            "year_level": row["year_level"]
        }
        for row in records
    ]


@anvil.server.callable(require_user=True)
def delete_registration(student_id):
    require_admin()

    student_id = (student_id or "").strip()

    if not student_id:
        raise ValueError("Student ID is required.")

    record = app_tables.students.get(
        student_id=student_id
    )

    if record is None:
        raise ValueError("Student record not found.")

    record.delete()

    return "Registration deleted successfully."


# ---------------------------------------------------------------------
# Supporting functions (not part of the activity's required code).
# Neither function accepts a role from the client.
# ---------------------------------------------------------------------

@anvil.server.callable(require_user=True)
def ensure_default_role():
    """Give brand-new accounts the Student role.
    Only fills an EMPTY role; it never changes Admin or any existing role,
    and the role value is fixed on the server (nothing comes from the client)."""
    user = anvil.users.get_user()
    if not user["role"]:
        user["role"] = "Student"
    return user["role"]


@anvil.server.callable(require_user=True)
def get_my_role():
    """Return the current user's role so the client can pick which view to
    request. Display only: the server re-checks the role on every operation."""
    user = anvil.users.get_user()
    return user["role"] or "Student"
