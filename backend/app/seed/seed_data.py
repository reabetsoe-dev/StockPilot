from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.user import User, UserRole
from app.services.audit_service import record_audit_log

DEMO_PASSWORD = "Demo123!"

DEPARTMENTS = [
    ("Procurement", "Supplier sourcing, purchase orders, and purchasing control."),
    ("Finance", "Budget review, purchasing accountability, and valuation oversight."),
    ("Information Technology", "Internal technology services and equipment requests."),
    ("Operations", "Cross-functional operations and stock coordination."),
    ("Administration", "Office administration and organization configuration."),
    ("Sales", "Customer-facing fulfillment and stock visibility."),
    ("Warehouse", "Receiving, storage, transfers, and stock issue operations."),
]

DEMO_USERS = [
    ("Avery Stone", "admin@stockpilot.local", UserRole.ADMINISTRATOR, "Administration"),
    ("Imani Jacobs", "inventory@stockpilot.local", UserRole.INVENTORY_MANAGER, "Operations"),
    ("Maya Chen", "procurement@stockpilot.local", UserRole.PROCUREMENT_OFFICER, "Procurement"),
    ("Thabo Mokoena", "warehouse@stockpilot.local", UserRole.WAREHOUSE_OFFICER, "Warehouse"),
    ("Lerato Ndlovu", "requester@stockpilot.local", UserRole.DEPARTMENT_REQUESTER, "Information Technology"),
    ("Jonah Price", "auditor@stockpilot.local", UserRole.AUDITOR, "Finance"),
    ("Priya Naidoo", "priya.naidoo@stockpilot.local", UserRole.INVENTORY_MANAGER, "Warehouse"),
    ("Sipho Dlamini", "sipho.dlamini@stockpilot.local", UserRole.PROCUREMENT_OFFICER, "Procurement"),
    ("Naledi Khumalo", "naledi.khumalo@stockpilot.local", UserRole.DEPARTMENT_REQUESTER, "Sales"),
    ("Marcus Reed", "marcus.reed@stockpilot.local", UserRole.WAREHOUSE_OFFICER, "Warehouse"),
]


def seed_departments(db: Session) -> dict[str, Department]:
    departments: dict[str, Department] = {}
    for name, description in DEPARTMENTS:
        department = db.scalar(select(Department).where(Department.name == name))
        if department is None:
            department = Department(name=name, description=description, active=True)
            db.add(department)
            db.flush()
        else:
            department.description = description
            department.active = True
        departments[name] = department
    return departments


def seed_users(db: Session, departments: dict[str, Department]) -> None:
    password_hash = get_password_hash(DEMO_PASSWORD)
    for full_name, email, role, department_name in DEMO_USERS:
        user = db.scalar(select(User).where(User.email == email))
        department = departments[department_name]
        if user is None:
            db.add(
                User(
                    full_name=full_name,
                    email=email,
                    role=role,
                    password_hash=password_hash,
                    department_id=department.id,
                    active=True,
                )
            )
        else:
            user.full_name = full_name
            user.role = role
            user.password_hash = password_hash
            user.department_id = department.id
            user.active = True


def seed_demo_data(db: Session) -> None:
    departments = seed_departments(db)
    seed_users(db, departments)
    db.flush()
    admin = db.scalar(select(User).where(User.email == "admin@stockpilot.local"))
    record_audit_log(
        db,
        admin,
        "DEMO_DATA_SEEDED",
        "System",
        None,
        "StockPilot Phase 1 demonstration organization was seeded.",
    )
    db.commit()


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        print("StockPilot demo accounts and departments seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
