from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.department import Department
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
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

CATEGORIES = [
    ("Electronics", "General electronic equipment, peripherals, and accessories."),
    ("Computers", "Laptops, workstations, monitors, storage, and computing hardware."),
    ("Networking", "Switches, cabling, routers, racks, and connectivity equipment."),
    ("Office Supplies", "Consumables used across office and administration teams."),
    ("Furniture", "Office furniture and fixtures for internal operations."),
    ("Cleaning Supplies", "Janitorial chemicals, hygiene products, and cleaning tools."),
    ("Vehicle Parts", "Service parts for company delivery and support vehicles."),
    ("Food & Beverages", "Breakroom, customer meeting, and staff refreshment supplies."),
]

WAREHOUSES = [
    ("CENTRAL", "Central Warehouse", "Maseru Industrial Area", "Primary receiving and bulk storage facility."),
    ("NORTH", "North Warehouse", "Leribe Logistics Park", "Regional storage for northern branch operations."),
    ("RETAIL", "Retail Store Warehouse", "Maseru CBD Retail Hub", "Forward stock location for retail and urgent issues."),
]

SUPPLIERS = [
    ("SUP-1001", "Apex Office Solutions", "Mpho Ralebese", "orders@apexoffice.example", "+266 5800 1001", "Net 30"),
    ("SUP-1002", "ByteBridge Technologies", "Kabelo Nkosi", "sales@bytebridge.example", "+266 5800 1002", "Net 15"),
    ("SUP-1003", "Metro Furniture Works", "Sarah Daniels", "accounts@metrofurniture.example", "+266 5800 1003", "Net 30"),
    ("SUP-1004", "CleanSphere Supplies", "Nomsa Mokoena", "service@cleansphere.example", "+266 5800 1004", "Due on receipt"),
    ("SUP-1005", "NetStack Distribution", "Ethan Price", "quotes@netstack.example", "+266 5800 1005", "Net 21"),
    ("SUP-1006", "FleetCare Parts", "Thabo Letsie", "parts@fleetcare.example", "+266 5800 1006", "Net 30"),
    ("SUP-1007", "PrintPro Consumables", "Lindiwe Jacobs", "orders@printpro.example", "+266 5800 1007", "Net 14"),
    ("SUP-1008", "SafeWork Industrial", "Sipho Molefe", "sales@safework.example", "+266 5800 1008", "Net 30"),
    ("SUP-1009", "FreshBreak Catering", "Aisha Patel", "hello@freshbreak.example", "+266 5800 1009", "Net 7"),
    ("SUP-1010", "DigitalDesk Hardware", "Daniel Mensah", "procure@digitaldesk.example", "+266 5800 1010", "Net 30"),
    ("SUP-1011", "PaperTrail Wholesale", "Naledi Sithole", "orders@papertrail.example", "+266 5800 1011", "Net 21"),
    ("SUP-1012", "Urban Warehouse Tools", "Andre Botha", "sales@urbanwarehouse.example", "+266 5800 1012", "Net 30"),
]

PRODUCTS = [
    ("LAP-HP-840", "100000000001", "HP EliteBook 840", "Business laptop with enterprise warranty.", "Computers", "Each", "14500.00", "17999.00", 5, "SUP-1010"),
    ("LAP-DELL-5450", "100000000002", "Dell Latitude 5450", "Reliable staff laptop for hybrid work.", "Computers", "Each", "15200.00", "18899.00", 10, "SUP-1002"),
    ("MON-DELL-24", "100000000003", "Dell Monitor 24 inch", "Full HD office monitor.", "Computers", "Each", "2250.00", "3199.00", 8, "SUP-1010"),
    ("MON-LG-27", "100000000004", "LG 27 inch IPS Monitor", "Large display for analysts and operations teams.", "Computers", "Each", "3600.00", "4599.00", 6, "SUP-1010"),
    ("MOU-LOGI-M185", "100000000005", "Logitech Wireless Mouse", "Compact wireless mouse for office users.", "Electronics", "Each", "190.00", "299.00", 20, "SUP-1002"),
    ("KEY-USB-STD", "100000000006", "USB Keyboard", "Standard full-size USB keyboard.", "Electronics", "Each", "210.00", "329.00", 20, "SUP-1002"),
    ("SSD-SAND-1TB", "100000000007", "External SSD 1TB", "Portable encrypted storage drive.", "Computers", "Each", "1350.00", "1799.00", 6, "SUP-1010"),
    ("USB-HUB-C", "100000000008", "USB-C Docking Hub", "Multi-port hub for laptops.", "Electronics", "Each", "580.00", "849.00", 10, "SUP-1002"),
    ("NET-CAT6-3M", "100000000009", "Cat6 Ethernet Cable 3m", "Patch cable for desks and network cabinets.", "Networking", "Each", "42.00", "79.00", 50, "SUP-1005"),
    ("NET-CAT6-10M", "100000000010", "Cat6 Ethernet Cable 10m", "Long patch cable for office moves.", "Networking", "Each", "95.00", "149.00", 40, "SUP-1005"),
    ("NET-SW-24", "100000000011", "Cisco-compatible Network Switch Demo Item", "24-port managed switch for branch networks.", "Networking", "Each", "4650.00", "6199.00", 3, "SUP-1005"),
    ("NET-ROUTER-BR", "100000000012", "Branch Router", "Secure router for small warehouse sites.", "Networking", "Each", "2750.00", "3699.00", 3, "SUP-1005"),
    ("NET-RACK-12U", "100000000013", "12U Wall Network Cabinet", "Wall-mounted network rack.", "Networking", "Each", "1650.00", "2299.00", 2, "SUP-1005"),
    ("PAP-A4-REAM", "100000000014", "A4 Printing Paper Ream", "White copier paper, 500 sheets.", "Office Supplies", "Ream", "55.00", "89.00", 120, "SUP-1011"),
    ("PAP-A4-BOX", "100000000015", "A4 Printing Paper Box", "Box of five A4 paper reams.", "Office Supplies", "Box", "260.00", "399.00", 30, "SUP-1011"),
    ("TON-HP-410", "100000000016", "HP Printer Toner 410A", "Black toner cartridge for office printers.", "Office Supplies", "Each", "890.00", "1199.00", 8, "SUP-1007"),
    ("TON-CAN-054", "100000000017", "Canon Toner 054", "Color toner cartridge for shared printers.", "Office Supplies", "Each", "760.00", "999.00", 6, "SUP-1007"),
    ("PEN-BALL-BLK", "100000000018", "Black Ballpoint Pens Pack", "Pack of 50 black pens.", "Office Supplies", "Pack", "85.00", "129.00", 25, "SUP-1001"),
    ("NBK-A5-12", "100000000019", "Notebook Pack A5", "Pack of 12 ruled notebooks.", "Office Supplies", "Pack", "115.00", "169.00", 20, "SUP-1001"),
    ("STP-STICKY", "100000000020", "Sticky Notes Multipack", "Assorted sticky notes for office use.", "Office Supplies", "Pack", "45.00", "79.00", 25, "SUP-1001"),
    ("CHR-ERG-01", "100000000021", "Ergonomic Office Chair", "Adjustable chair for staff workstations.", "Furniture", "Each", "1750.00", "2499.00", 6, "SUP-1003"),
    ("DSK-1400-OAK", "100000000022", "Office Desk 1400mm", "Durable office desk with cable routing.", "Furniture", "Each", "2100.00", "2899.00", 4, "SUP-1003"),
    ("CAB-FILE-4D", "100000000023", "Four Drawer Filing Cabinet", "Lockable document cabinet.", "Furniture", "Each", "1850.00", "2599.00", 3, "SUP-1003"),
    ("TBL-MEET-8", "100000000024", "Eight Seat Meeting Table", "Boardroom table for meeting spaces.", "Furniture", "Each", "5200.00", "6999.00", 1, "SUP-1003"),
    ("CLN-DISINF-5L", "100000000025", "Disinfectant Cleaner 5L", "Multi-surface disinfectant concentrate.", "Cleaning Supplies", "Bottle", "130.00", "199.00", 15, "SUP-1004"),
    ("CLN-HAND-5L", "100000000026", "Hand Sanitizer 5L", "Bulk sanitizer refill.", "Cleaning Supplies", "Bottle", "155.00", "229.00", 12, "SUP-1004"),
    ("CLN-MOP-SET", "100000000027", "Industrial Mop Set", "Mop handle, head, and bucket set.", "Cleaning Supplies", "Set", "310.00", "459.00", 8, "SUP-1004"),
    ("CLN-TRASH-BAG", "100000000028", "Heavy Duty Trash Bags", "Pack of 100 refuse bags.", "Cleaning Supplies", "Pack", "95.00", "149.00", 20, "SUP-1004"),
    ("SAFE-GLOVE-NIT", "100000000029", "Nitrile Safety Gloves Box", "Disposable nitrile gloves.", "Cleaning Supplies", "Box", "120.00", "189.00", 25, "SUP-1008"),
    ("SAFE-GLOVE-IND", "100000000030", "Industrial Safety Gloves", "Reusable warehouse handling gloves.", "Cleaning Supplies", "Pair", "38.00", "65.00", 50, "SUP-1008"),
    ("SAFE-VEST-REF", "100000000031", "Reflective Safety Vest", "High-visibility vest for warehouse staff.", "Cleaning Supplies", "Each", "90.00", "139.00", 25, "SUP-1008"),
    ("SAFE-BOOT-STD", "100000000032", "Safety Boots", "Steel-toe boots for warehouse work.", "Cleaning Supplies", "Pair", "480.00", "699.00", 10, "SUP-1008"),
    ("VEH-OIL-FLT", "100000000033", "Vehicle Oil Filter", "Oil filter for delivery fleet service.", "Vehicle Parts", "Each", "120.00", "189.00", 12, "SUP-1006"),
    ("VEH-AIR-FLT", "100000000034", "Vehicle Air Filter", "Replacement air filter for fleet vehicles.", "Vehicle Parts", "Each", "145.00", "219.00", 10, "SUP-1006"),
    ("VEH-BRK-PAD", "100000000035", "Brake Pad Set", "Brake pad set for light commercial vehicles.", "Vehicle Parts", "Set", "520.00", "749.00", 6, "SUP-1006"),
    ("VEH-WIPER-22", "100000000036", "Wiper Blade 22 inch", "Replacement wiper blade.", "Vehicle Parts", "Each", "95.00", "149.00", 12, "SUP-1006"),
    ("VEH-BAT-12V", "100000000037", "12V Vehicle Battery", "Battery for delivery vehicles.", "Vehicle Parts", "Each", "1350.00", "1799.00", 3, "SUP-1006"),
    ("FOOD-COF-1KG", "100000000038", "Coffee Beans 1kg", "Office coffee beans for staff kitchens.", "Food & Beverages", "Bag", "210.00", "299.00", 10, "SUP-1009"),
    ("FOOD-TEA-100", "100000000039", "Rooibos Tea Box", "Box of 100 tea bags.", "Food & Beverages", "Box", "75.00", "119.00", 12, "SUP-1009"),
    ("FOOD-SUGAR-5KG", "100000000040", "White Sugar 5kg", "Bulk sugar for staff kitchens.", "Food & Beverages", "Bag", "95.00", "139.00", 10, "SUP-1009"),
    ("FOOD-WATER-24", "100000000041", "Bottled Water Case", "24-pack still water case.", "Food & Beverages", "Case", "120.00", "169.00", 20, "SUP-1009"),
    ("ELEC-UPS-1000", "100000000042", "UPS 1000VA", "Backup power unit for critical desks.", "Electronics", "Each", "1450.00", "1999.00", 5, "SUP-1002"),
    ("ELEC-EXT-6WAY", "100000000043", "Six-Way Extension Lead", "Surge-protected extension lead.", "Electronics", "Each", "180.00", "279.00", 15, "SUP-1002"),
    ("ELEC-HDMI-2M", "100000000044", "HDMI Cable 2m", "Presentation and monitor cable.", "Electronics", "Each", "65.00", "109.00", 20, "SUP-1002"),
    ("TOOL-PALLET-JACK", "100000000045", "Manual Pallet Jack", "Warehouse pallet handling tool.", "Furniture", "Each", "4200.00", "5599.00", 2, "SUP-1012"),
    ("TOOL-BARCODE-SC", "100000000046", "USB Barcode Scanner", "Handheld scanner for stock processing.", "Electronics", "Each", "820.00", "1199.00", 4, "SUP-1012"),
    ("TOOL-LABEL-PR", "100000000047", "Thermal Label Printer", "Warehouse label printer.", "Electronics", "Each", "1950.00", "2699.00", 3, "SUP-1012"),
    ("PACK-TAPE-48", "100000000048", "Packaging Tape 48mm", "Carton sealing tape.", "Office Supplies", "Roll", "28.00", "49.00", 50, "SUP-1012"),
    ("PACK-BUBBLE-50", "100000000049", "Bubble Wrap Roll 50m", "Protective packaging roll.", "Office Supplies", "Roll", "310.00", "449.00", 8, "SUP-1012"),
    ("PACK-CARTON-M", "100000000050", "Medium Shipping Carton", "Standard medium carton for dispatch.", "Office Supplies", "Each", "18.00", "32.00", 100, "SUP-1012"),
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


def seed_categories(db: Session) -> dict[str, Category]:
    categories: dict[str, Category] = {}
    for name, description in CATEGORIES:
        category = db.scalar(select(Category).where(Category.name == name))
        if category is None:
            category = Category(name=name, description=description, active=True)
            db.add(category)
            db.flush()
        else:
            category.description = description
            category.active = True
        categories[name] = category
    return categories


def seed_warehouses(db: Session) -> dict[str, Warehouse]:
    warehouses: dict[str, Warehouse] = {}
    for code, name, location, description in WAREHOUSES:
        warehouse = db.scalar(select(Warehouse).where(Warehouse.code == code))
        if warehouse is None:
            warehouse = Warehouse(code=code, name=name, location=location, description=description, active=True)
            db.add(warehouse)
            db.flush()
        else:
            warehouse.name = name
            warehouse.location = location
            warehouse.description = description
            warehouse.active = True
        warehouses[code] = warehouse
    return warehouses


def seed_suppliers(db: Session) -> dict[str, Supplier]:
    suppliers: dict[str, Supplier] = {}
    for code, name, contact_person, email, phone, payment_terms in SUPPLIERS:
        supplier = db.scalar(select(Supplier).where(Supplier.supplier_code == code))
        if supplier is None:
            supplier = Supplier(
                supplier_code=code,
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=f"{name}, Demo Business Park, Maseru",
                tax_reference=f"TAX-{code}",
                payment_terms=payment_terms,
                active=True,
            )
            db.add(supplier)
            db.flush()
        else:
            supplier.name = name
            supplier.contact_person = contact_person
            supplier.email = email
            supplier.phone = phone
            supplier.address = f"{name}, Demo Business Park, Maseru"
            supplier.tax_reference = f"TAX-{code}"
            supplier.payment_terms = payment_terms
            supplier.active = True
        suppliers[code] = supplier
    return suppliers


def seed_products(db: Session, categories: dict[str, Category], suppliers: dict[str, Supplier]) -> None:
    for sku, barcode, name, description, category_name, unit, cost_price, selling_price, reorder_level, supplier_code in PRODUCTS:
        product = db.scalar(select(Product).where(Product.sku == sku))
        category = categories[category_name]
        supplier = suppliers[supplier_code]
        if product is None:
            db.add(
                Product(
                    sku=sku,
                    barcode=barcode,
                    name=name,
                    description=description,
                    category_id=category.id,
                    unit_of_measure=unit,
                    cost_price=cost_price,
                    selling_price=selling_price,
                    reorder_level=reorder_level,
                    preferred_supplier_id=supplier.id,
                    active=True,
                )
            )
        else:
            product.barcode = barcode
            product.name = name
            product.description = description
            product.category_id = category.id
            product.unit_of_measure = unit
            product.cost_price = cost_price
            product.selling_price = selling_price
            product.reorder_level = reorder_level
            product.preferred_supplier_id = supplier.id
            product.active = True


def seed_demo_data(db: Session) -> None:
    departments = seed_departments(db)
    seed_users(db, departments)
    categories = seed_categories(db)
    seed_warehouses(db)
    suppliers = seed_suppliers(db)
    seed_products(db, categories, suppliers)
    db.flush()
    admin = db.scalar(select(User).where(User.email == "admin@stockpilot.local"))
    record_audit_log(
        db,
        admin,
        "DEMO_DATA_SEEDED",
        "System",
        None,
        "StockPilot demonstration organization and catalog records were seeded.",
    )
    db.commit()


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        print("StockPilot demo accounts, departments, and catalog records seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
