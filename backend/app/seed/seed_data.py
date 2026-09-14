from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.models.base import utc_now
from app.models.category import Category
from app.models.department import Department
from app.models.inventory import StockMovement, StockMovementType
from app.models.notification import Notification
from app.models.procurement import (
    GoodsReceipt,
    GoodsReceiptItem,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseRequestPriority,
    PurchaseRequestStatus,
)
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User, UserRole
from app.models.warehouse import Warehouse
from app.models.warehouse_ops import (
    StockAdjustment,
    StockAdjustmentType,
    StockRequest,
    StockRequestItem,
    StockRequestStatus,
    StockTransfer,
    StockTransferItem,
    StockTransferStatus,
)
from app.services.audit_service import record_audit_log
from app.services.inventory_service import record_opening_balance
from app.services.notification_service import create_notification

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
    ("Grace Moloi", "grace.moloi@stockpilot.local", UserRole.ADMINISTRATOR, "Finance"),
    ("Palesa Radebe", "palesa.radebe@stockpilot.local", UserRole.INVENTORY_MANAGER, "Warehouse"),
    ("Owen Carter", "owen.carter@stockpilot.local", UserRole.PROCUREMENT_OFFICER, "Procurement"),
    ("Mpho Letsie", "mpho.letsie@stockpilot.local", UserRole.WAREHOUSE_OFFICER, "Warehouse"),
    ("Anika Pillay", "anika.pillay@stockpilot.local", UserRole.DEPARTMENT_REQUESTER, "Administration"),
    ("Tumi Sekete", "tumi.sekete@stockpilot.local", UserRole.DEPARTMENT_REQUESTER, "Operations"),
    ("Ethan Wright", "ethan.wright@stockpilot.local", UserRole.DEPARTMENT_REQUESTER, "Sales"),
    ("Zara Maseko", "zara.maseko@stockpilot.local", UserRole.AUDITOR, "Finance"),
    ("Nate Foster", "nate.foster@stockpilot.local", UserRole.INVENTORY_MANAGER, "Operations"),
    ("Keabetswe Dube", "keabetswe.dube@stockpilot.local", UserRole.PROCUREMENT_OFFICER, "Procurement"),
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

OPENING_STOCK_OVERRIDES: dict[str, list[tuple[str, int, int]]] = {
    "LAP-HP-840": [("CENTRAL", 4, 1), ("NORTH", 1, 0), ("RETAIL", 0, 0)],
    "NET-SW-24": [("CENTRAL", 2, 0), ("NORTH", 0, 0), ("RETAIL", 0, 0)],
    "NET-RACK-12U": [("CENTRAL", 0, 0), ("NORTH", 0, 0), ("RETAIL", 0, 0)],
    "TBL-MEET-8": [("CENTRAL", 0, 0), ("NORTH", 0, 0), ("RETAIL", 0, 0)],
    "VEH-BAT-12V": [("CENTRAL", 2, 0), ("NORTH", 0, 0), ("RETAIL", 0, 0)],
    "TOOL-PALLET-JACK": [("CENTRAL", 1, 0), ("NORTH", 0, 0), ("RETAIL", 0, 0)],
}

REQUEST_PURPOSES = [
    "Replace aging laptops for hybrid operations staff.",
    "Restock paper and toner for finance month-end reporting.",
    "Network cabinet refresh for the north warehouse.",
    "Office seating for the expanded procurement team.",
    "Warehouse safety consumables for the next quarter.",
    "Delivery fleet service parts for scheduled maintenance.",
    "Refresh breakroom supplies for customer workshops.",
    "Barcode equipment for receiving accuracy.",
    "Packaging materials for retail dispatch growth.",
    "Monitor upgrade for analytics workstations.",
    "Emergency UPS cover for branch routers.",
    "Cleaning supplies for peak-season warehouse shifts.",
    "Stationery pack for onboarding new employees.",
    "Replacement keyboards and mice for shared desks.",
    "Meeting room furniture for supplier reviews.",
    "Network cabling for office moves.",
    "Toner reserve for sales proposal printing.",
    "Pallet handling tool replacement.",
    "Safety boots for new warehouse team members.",
    "Vehicle battery reserve for delivery fleet.",
    "External SSDs for secure field backups.",
    "Shipping cartons for ecommerce dispatch.",
]

PURCHASE_ORDER_SKUS = [
    ["LAP-HP-840", "MON-DELL-24"],
    ["PAP-A4-REAM", "TON-HP-410"],
    ["NET-SW-24", "NET-CAT6-10M"],
    ["CHR-ERG-01", "DSK-1400-OAK"],
    ["SAFE-GLOVE-IND", "SAFE-VEST-REF"],
    ["VEH-OIL-FLT", "VEH-AIR-FLT"],
    ["FOOD-COF-1KG", "FOOD-WATER-24"],
    ["TOOL-BARCODE-SC", "TOOL-LABEL-PR"],
    ["PACK-CARTON-M", "PACK-TAPE-48"],
    ["MON-LG-27", "SSD-SAND-1TB"],
    ["ELEC-UPS-1000", "ELEC-EXT-6WAY"],
    ["CLN-DISINF-5L", "CLN-HAND-5L"],
    ["NBK-A5-12", "PEN-BALL-BLK"],
    ["MOU-LOGI-M185", "KEY-USB-STD"],
    ["CAB-FILE-4D", "TBL-MEET-8"],
    ["NET-CAT6-3M", "NET-ROUTER-BR"],
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


def seed_products(db: Session, categories: dict[str, Category], suppliers: dict[str, Supplier]) -> dict[str, Product]:
    products: dict[str, Product] = {}
    for sku, barcode, name, description, category_name, unit, cost_price, selling_price, reorder_level, supplier_code in PRODUCTS:
        product = db.scalar(select(Product).where(Product.sku == sku))
        category = categories[category_name]
        supplier = suppliers[supplier_code]
        if product is None:
            product = Product(
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
            db.add(product)
            db.flush()
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
        products[sku] = product
    return products


def opening_stock_rows(sku: str, index: int, reorder_level: int) -> list[tuple[str, int, int]]:
    if sku in OPENING_STOCK_OVERRIDES:
        return OPENING_STOCK_OVERRIDES[sku]

    central = reorder_level * 3 + 18 + (index % 9) * 4
    north = reorder_level + 8 + (index % 6) * 3
    retail = max(0, (reorder_level // 2) + (index % 5) * 2)
    reserved_seed = index % 4
    central_reserved = min(reserved_seed, central)
    north_reserved = min(1 if index % 7 == 0 else 0, north)
    return [
        ("CENTRAL", central, central_reserved),
        ("NORTH", north, north_reserved),
        ("RETAIL", retail, 0),
    ]


def seed_opening_inventory(
    db: Session,
    products: dict[str, Product],
    warehouses: dict[str, Warehouse],
    actor: User | None,
) -> None:
    reorder_levels = {sku: reorder_level for sku, _, _, _, _, _, _, _, reorder_level, _ in PRODUCTS}
    for index, (sku, *_rest) in enumerate(PRODUCTS, start=1):
        product = products[sku]
        for warehouse_code, quantity_on_hand, quantity_reserved in opening_stock_rows(sku, index, reorder_levels[sku]):
            record_opening_balance(
                db,
                product,
                warehouses[warehouse_code],
                quantity_on_hand,
                quantity_reserved,
                actor,
            )


def user_by_email(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        raise RuntimeError(f"Seed user {email} was not created.")
    return user


def movement_exists(db: Session, reference_type: str, reference_id: str, movement_type: StockMovementType) -> bool:
    return db.scalar(
        select(StockMovement).where(
            StockMovement.reference_type == reference_type,
            StockMovement.reference_id == reference_id,
            StockMovement.movement_type == movement_type,
        )
    ) is not None


def seed_purchase_requests(
    db: Session,
    departments: dict[str, Department],
    products: dict[str, Product],
    requesters: list[User],
) -> dict[str, PurchaseRequest]:
    year = date.today().year
    statuses = [
        PurchaseRequestStatus.DRAFT,
        PurchaseRequestStatus.SUBMITTED,
        PurchaseRequestStatus.APPROVED,
        PurchaseRequestStatus.REJECTED,
    ]
    priorities = [
        PurchaseRequestPriority.NORMAL,
        PurchaseRequestPriority.HIGH,
        PurchaseRequestPriority.URGENT,
        PurchaseRequestPriority.LOW,
    ]
    department_cycle = ["Information Technology", "Operations", "Sales", "Administration", "Warehouse"]
    product_values = list(products.values())
    requests: dict[str, PurchaseRequest] = {}
    for index, purpose in enumerate(REQUEST_PURPOSES, start=1):
        reference = f"PR-{year}-{index:04d}"
        request = db.scalar(select(PurchaseRequest).where(PurchaseRequest.reference_number == reference))
        requester = requesters[(index - 1) % len(requesters)]
        department = departments[department_cycle[(index - 1) % len(department_cycle)]]
        if request is None:
            request = PurchaseRequest(
                reference_number=reference,
                requested_by=requester.id,
                department_id=department.id,
                purpose=purpose,
                priority=priorities[(index - 1) % len(priorities)],
                status=statuses[(index - 1) % len(statuses)],
            )
            db.add(request)
            db.flush()
            for item_offset in range(2):
                product = product_values[(index * 3 + item_offset) % len(product_values)]
                db.add(
                    PurchaseRequestItem(
                        purchase_request_id=request.id,
                        product_id=product.id,
                        description=product.name,
                        quantity=2 + ((index + item_offset) % 8),
                        estimated_unit_price=product.cost_price,
                    )
                )
        else:
            request.requested_by = requester.id
            request.department_id = department.id
            request.purpose = purpose
            request.priority = priorities[(index - 1) % len(priorities)]
            if request.status not in {PurchaseRequestStatus.CONVERTED_TO_PO}:
                request.status = statuses[(index - 1) % len(statuses)]
        requests[reference] = request
    return requests


def seed_purchase_orders(
    db: Session,
    products: dict[str, Product],
    suppliers: dict[str, Supplier],
    purchase_requests: dict[str, PurchaseRequest],
    actor: User,
) -> dict[str, PurchaseOrder]:
    year = date.today().year
    supplier_values = list(suppliers.values())
    orders: dict[str, PurchaseOrder] = {}
    for index, skus in enumerate(PURCHASE_ORDER_SKUS, start=1):
        reference = f"PO-{year}-{index:04d}"
        order = db.scalar(select(PurchaseOrder).where(PurchaseOrder.po_number == reference))
        supplier = supplier_values[(index - 1) % len(supplier_values)]
        linked_request = purchase_requests.get(f"PR-{year}-{index:04d}")
        if order is None:
            order = PurchaseOrder(
                po_number=reference,
                supplier_id=supplier.id,
                purchase_request_id=linked_request.id if linked_request else None,
                order_date=date.today() - timedelta(days=30 - index),
                expected_delivery_date=date.today() + timedelta(days=index % 12),
                status=PurchaseOrderStatus.ISSUED,
                notes="Seeded portfolio purchase order.",
                created_by=actor.id,
            )
            db.add(order)
            db.flush()
            subtotal = Decimal("0.00")
            for item_offset, sku in enumerate(skus):
                product = products[sku]
                quantity = 8 + index + item_offset * 3
                unit_price = Decimal(product.cost_price)
                line_total = (Decimal(quantity) * unit_price).quantize(Decimal("0.01"))
                subtotal += line_total
                db.add(
                    PurchaseOrderItem(
                        purchase_order_id=order.id,
                        product_id=product.id,
                        description=product.name,
                        quantity_ordered=quantity,
                        quantity_received=0,
                        unit_price=unit_price,
                        line_total=line_total,
                    )
                )
            order.subtotal = subtotal.quantize(Decimal("0.01"))
            order.tax = (order.subtotal * Decimal("0.15")).quantize(Decimal("0.01"))
            order.total = (order.subtotal + order.tax).quantize(Decimal("0.01"))
        else:
            order.supplier_id = supplier.id
        if linked_request and linked_request.status == PurchaseRequestStatus.APPROVED:
            linked_request.status = PurchaseRequestStatus.CONVERTED_TO_PO
        orders[reference] = order
    return orders


def seed_goods_receipts(
    db: Session,
    purchase_orders: dict[str, PurchaseOrder],
    warehouses: dict[str, Warehouse],
    actor: User,
) -> None:
    year = date.today().year
    for index, reference in enumerate(list(purchase_orders.keys())[:8], start=1):
        receipt_number = f"GRN-{year}-{index:04d}"
        if db.scalar(select(GoodsReceipt).where(GoodsReceipt.receipt_number == receipt_number)) is not None:
            continue
        order = db.scalar(
            select(PurchaseOrder)
            .where(PurchaseOrder.id == purchase_orders[reference].id)
            .options(selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.product))
        )
        warehouse = warehouses["CENTRAL" if index % 2 else "NORTH"]
        receipt = GoodsReceipt(
            receipt_number=receipt_number,
            purchase_order_id=order.id,
            warehouse_id=warehouse.id,
            received_by=actor.id,
            received_date=date.today() - timedelta(days=8 - index),
            notes="Seeded goods receipt for portfolio demo history.",
        )
        db.add(receipt)
        db.flush()
        for item in order.items:
            receive_quantity = item.quantity_ordered if index > 3 else max(1, item.quantity_ordered // 2)
            item.quantity_received += receive_quantity
            db.add(
                GoodsReceiptItem(
                    goods_receipt_id=receipt.id,
                    purchase_order_item_id=item.id,
                    product_id=item.product_id,
                    quantity_received=receive_quantity,
                    quantity_rejected=0,
                    notes="Accepted into warehouse stock.",
                )
            )
            if not db.scalar(
                select(StockMovement).where(
                    StockMovement.reference_type == "GOODS_RECEIPT",
                    StockMovement.reference_id == receipt_number,
                    StockMovement.product_id == item.product_id,
                    StockMovement.warehouse_id == warehouse.id,
                    StockMovement.movement_type == StockMovementType.GOODS_RECEIPT,
                )
            ):
                from app.services.inventory_service import record_stock_movement

                record_stock_movement(
                    db,
                    item.product,
                    warehouse,
                    StockMovementType.GOODS_RECEIPT,
                    receive_quantity,
                    actor,
                    "GOODS_RECEIPT",
                    receipt_number,
                    f"Seeded receipt against {order.po_number}.",
                )
        order.status = (
            PurchaseOrderStatus.RECEIVED
            if all(item.quantity_received >= item.quantity_ordered for item in order.items)
            else PurchaseOrderStatus.PARTIALLY_RECEIVED
        )


def seed_stock_requests(
    db: Session,
    departments: dict[str, Department],
    products: dict[str, Product],
    warehouses: dict[str, Warehouse],
    requesters: list[User],
    actor: User,
) -> None:
    from app.services.inventory_service import record_stock_movement

    year = date.today().year
    stock_skus = ["PAP-A4-REAM", "PEN-BALL-BLK", "MOU-LOGI-M185", "KEY-USB-STD", "PACK-CARTON-M", "SAFE-VEST-REF"]
    for index in range(1, 13):
        reference = f"SR-{year}-{index:04d}"
        request = db.scalar(select(StockRequest).where(StockRequest.reference_number == reference))
        requester = requesters[(index - 1) % len(requesters)]
        if request is None:
            request = StockRequest(
                reference_number=reference,
                department_id=departments[["Information Technology", "Sales", "Operations", "Administration"][index % 4]].id,
                requested_by=requester.id,
                source_warehouse_id=warehouses["CENTRAL"].id,
                purpose=f"Internal stock issue for department operating request {index}.",
                status=StockRequestStatus.ISSUED if index <= 5 else (StockRequestStatus.APPROVED if index <= 8 else StockRequestStatus.SUBMITTED),
                issued_by=actor.id if index <= 5 else None,
                issued_at=utc_now() if index <= 5 else None,
            )
            db.add(request)
            db.flush()
            for offset in range(2):
                product = products[stock_skus[(index + offset) % len(stock_skus)]]
                requested_quantity = 2 + ((index + offset) % 5)
                item = StockRequestItem(
                    stock_request_id=request.id,
                    product_id=product.id,
                    quantity_requested=requested_quantity,
                    quantity_issued=requested_quantity if index <= 5 else 0,
                )
                db.add(item)
                if index <= 5 and not db.scalar(
                    select(StockMovement).where(
                        StockMovement.reference_type == "STOCK_REQUEST",
                        StockMovement.reference_id == reference,
                        StockMovement.product_id == product.id,
                        StockMovement.movement_type == StockMovementType.STOCK_ISSUE,
                    )
                ):
                    record_stock_movement(
                        db,
                        product,
                        warehouses["CENTRAL"],
                        StockMovementType.STOCK_ISSUE,
                        requested_quantity,
                        actor,
                        "STOCK_REQUEST",
                        reference,
                        f"Seeded issue for {reference}.",
                    )


def seed_transfers(
    db: Session,
    products: dict[str, Product],
    warehouses: dict[str, Warehouse],
    actor: User,
) -> None:
    from app.services.inventory_service import record_stock_movement

    year = date.today().year
    transfer_skus = ["PAP-A4-REAM", "NET-CAT6-3M", "PACK-CARTON-M", "SAFE-GLOVE-IND", "FOOD-WATER-24", "ELEC-HDMI-2M"]
    for index, sku in enumerate(transfer_skus, start=1):
        reference = f"TRF-{year}-{index:04d}"
        transfer = db.scalar(select(StockTransfer).where(StockTransfer.transfer_number == reference))
        if transfer is None:
            status_value = StockTransferStatus.COMPLETED if index <= 4 else (StockTransferStatus.IN_TRANSIT if index == 5 else StockTransferStatus.DRAFT)
            transfer = StockTransfer(
                transfer_number=reference,
                source_warehouse_id=warehouses["CENTRAL"].id,
                destination_warehouse_id=warehouses["NORTH" if index % 2 else "RETAIL"].id,
                status=status_value,
                requested_by=actor.id,
                completed_by=actor.id if status_value == StockTransferStatus.COMPLETED else None,
                completed_at=utc_now() if status_value == StockTransferStatus.COMPLETED else None,
            )
            db.add(transfer)
            db.flush()
            product = products[sku]
            quantity = 3 + index
            db.add(StockTransferItem(stock_transfer_id=transfer.id, product_id=product.id, quantity=quantity))
            if status_value in {StockTransferStatus.COMPLETED, StockTransferStatus.IN_TRANSIT} and not db.scalar(
                select(StockMovement).where(
                    StockMovement.reference_type == "STOCK_TRANSFER",
                    StockMovement.reference_id == reference,
                    StockMovement.movement_type == StockMovementType.TRANSFER_OUT,
                )
            ):
                record_stock_movement(
                    db,
                    product,
                    warehouses["CENTRAL"],
                    StockMovementType.TRANSFER_OUT,
                    quantity,
                    actor,
                    "STOCK_TRANSFER",
                    reference,
                    "Seeded transfer dispatch.",
                )
            if status_value == StockTransferStatus.COMPLETED and not db.scalar(
                select(StockMovement).where(
                    StockMovement.reference_type == "STOCK_TRANSFER",
                    StockMovement.reference_id == reference,
                    StockMovement.movement_type == StockMovementType.TRANSFER_IN,
                )
            ):
                record_stock_movement(
                    db,
                    product,
                    warehouses["NORTH" if index % 2 else "RETAIL"],
                    StockMovementType.TRANSFER_IN,
                    quantity,
                    actor,
                    "STOCK_TRANSFER",
                    reference,
                    "Seeded transfer receipt.",
                )


def seed_adjustments(
    db: Session,
    products: dict[str, Product],
    warehouses: dict[str, Warehouse],
    actor: User,
) -> None:
    from app.services.inventory_service import record_stock_movement

    year = date.today().year
    adjustments = [
        ("ADJ", "CLN-DISINF-5L", "CENTRAL", StockAdjustmentType.INCREASE, 6, "Cycle count found additional sealed bottles."),
        ("ADJ", "PACK-TAPE-48", "CENTRAL", StockAdjustmentType.DECREASE, 4, "Damaged rolls removed from available stock."),
        ("ADJ", "FOOD-COF-1KG", "NORTH", StockAdjustmentType.INCREASE, 3, "Branch returned unopened coffee stock."),
        ("ADJ", "SAFE-GLOVE-IND", "CENTRAL", StockAdjustmentType.DECREASE, 5, "Warehouse gloves written off after inspection."),
        ("ADJ", "ELEC-HDMI-2M", "RETAIL", StockAdjustmentType.INCREASE, 2, "Recovered cables from meeting-room setup."),
    ]
    for index, (_, sku, warehouse_code, adjustment_type, quantity, reason) in enumerate(adjustments, start=1):
        reference = f"ADJ-{year}-{index:04d}"
        if db.scalar(select(StockAdjustment).where(StockAdjustment.adjustment_number == reference)) is not None:
            continue
        product = products[sku]
        warehouse = warehouses[warehouse_code]
        adjustment = StockAdjustment(
            adjustment_number=reference,
            product_id=product.id,
            warehouse_id=warehouse.id,
            adjustment_type=adjustment_type,
            quantity=quantity,
            reason=reason,
            notes="Seeded stock adjustment for audit trail demonstration.",
            performed_by=actor.id,
        )
        db.add(adjustment)
        movement_type = StockMovementType.ADJUSTMENT_INCREASE if adjustment_type == StockAdjustmentType.INCREASE else StockMovementType.ADJUSTMENT_DECREASE
        record_stock_movement(db, product, warehouse, movement_type, quantity, actor, "STOCK_ADJUSTMENT", reference, reason)


def seed_notifications(db: Session, users: dict[str, User]) -> None:
    notifications = [
        ("Low stock review", "Several products are at or below reorder level.", users["inventory@stockpilot.local"].id, "LowStock", None, "/low-stock"),
        ("PO delivery watch", "Open purchase orders are awaiting warehouse receipt.", users["warehouse@stockpilot.local"].id, "PurchaseOrder", None, "/goods-receiving"),
        ("Supplier follow-up", "Partially received purchase orders need procurement follow-up.", users["procurement@stockpilot.local"].id, "PurchaseOrder", None, "/purchase-orders"),
        ("Audit snapshot ready", "Stock movements and adjustments are available for audit review.", users["auditor@stockpilot.local"].id, "AuditLog", None, "/audit-logs"),
    ]
    for title, message, user_id, entity_type, entity_id, action_url in notifications:
        if db.scalar(select(Notification).where(Notification.title == title, Notification.user_id == user_id)) is None:
            create_notification(db, title, message, user_id, entity_type, entity_id, action_url)


def seed_demo_data(db: Session) -> None:
    departments = seed_departments(db)
    seed_users(db, departments)
    categories = seed_categories(db)
    warehouses = seed_warehouses(db)
    suppliers = seed_suppliers(db)
    products = seed_products(db, categories, suppliers)
    db.flush()
    admin = db.scalar(select(User).where(User.email == "admin@stockpilot.local"))
    users_by_email = {email: user_by_email(db, email) for _, email, _, _ in DEMO_USERS}
    requesters = [
        users_by_email["requester@stockpilot.local"],
        users_by_email["naledi.khumalo@stockpilot.local"],
        users_by_email["anika.pillay@stockpilot.local"],
        users_by_email["tumi.sekete@stockpilot.local"],
        users_by_email["ethan.wright@stockpilot.local"],
    ]
    seed_opening_inventory(db, products, warehouses, admin)
    purchase_requests = seed_purchase_requests(db, departments, products, requesters)
    purchase_orders = seed_purchase_orders(db, products, suppliers, purchase_requests, users_by_email["procurement@stockpilot.local"])
    db.flush()
    seed_goods_receipts(db, purchase_orders, warehouses, users_by_email["warehouse@stockpilot.local"])
    seed_stock_requests(db, departments, products, warehouses, requesters, users_by_email["warehouse@stockpilot.local"])
    seed_transfers(db, products, warehouses, users_by_email["warehouse@stockpilot.local"])
    seed_adjustments(db, products, warehouses, users_by_email["inventory@stockpilot.local"])
    seed_notifications(db, users_by_email)
    record_audit_log(
        db,
        admin,
        "DEMO_DATA_SEEDED",
        "System",
        None,
        "StockPilot demonstration organization, catalog, workflows, and stock ledger were seeded.",
    )
    db.commit()


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
        print("StockPilot demo accounts, catalog, workflows, and stock ledger seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
