from typing import Any

# These definitions are copied into each new business as editable starting templates.
# They are data-entry schemas, not claims that any particular record already exists.
TEMPLATE_DEFINITIONS: dict[str, list[dict[str, Any]]] = {
    "restaurant": [
        {
            "key": "daily_sales", "name": "Daily Sales", "description": "Sales totals and payment breakdowns.",
            "fields": [
                {"key": "date", "label": "Business date", "type": "date", "required": True},
                {"key": "gross_amount", "label": "Gross sales", "type": "money", "required": True},
                {"key": "payment_method", "label": "Payment method", "type": "select", "required": True, "options": ["cash", "transfer", "card", "other"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "purchases", "name": "Purchases", "description": "Ingredients and other items bought by the restaurant.",
            "fields": [
                {"key": "date", "label": "Purchase date", "type": "date", "required": True},
                {"key": "supplier", "label": "Supplier", "type": "text", "required": True},
                {"key": "item", "label": "Item", "type": "text", "required": True},
                {"key": "quantity", "label": "Quantity", "type": "number", "required": True},
                {"key": "amount", "label": "Total cost", "type": "money", "required": True},
            ],
        },
        {
            "key": "stock_movements", "name": "Stock Movements", "description": "Ingredients received, used, transferred, or adjusted.",
            "fields": [
                {"key": "date", "label": "Date", "type": "date", "required": True},
                {"key": "item", "label": "Ingredient or item", "type": "text", "required": True},
                {"key": "movement", "label": "Movement", "type": "select", "required": True, "options": ["received", "used", "transfer", "adjustment"]},
                {"key": "quantity", "label": "Quantity", "type": "number", "required": True},
            ],
        },
        {
            "key": "waste", "name": "Waste", "description": "Spoiled, damaged, or discarded ingredients and food.",
            "fields": [
                {"key": "date", "label": "Date", "type": "date", "required": True},
                {"key": "item", "label": "Item", "type": "text", "required": True},
                {"key": "quantity", "label": "Quantity", "type": "number", "required": True},
                {"key": "reason", "label": "Reason", "type": "text", "required": True},
            ],
        },
        {
            "key": "expenses", "name": "Expenses", "description": "Operating costs such as utilities, rent, and transport.",
            "fields": [
                {"key": "date", "label": "Date", "type": "date", "required": True},
                {"key": "category", "label": "Category", "type": "text", "required": True},
                {"key": "amount", "label": "Amount", "type": "money", "required": True},
                {"key": "description", "label": "Description", "type": "text", "required": False},
            ],
        },
        {
            "key": "payments", "name": "Payments", "description": "Payments received and outgoing payments recorded separately from sales.",
            "fields": [
                {"key": "date", "label": "Date", "type": "date", "required": True},
                {"key": "direction", "label": "Direction", "type": "select", "required": True, "options": ["incoming", "outgoing"]},
                {"key": "amount", "label": "Amount", "type": "money", "required": True},
                {"key": "reference", "label": "Reference", "type": "text", "required": False},
            ],
        },
    ],
    "supermarket": [
        {
            "key": "products", "name": "Products", "description": "Product catalogue and stock identifiers.",
            "fields": [
                {"key": "sku", "label": "SKU or product code", "type": "text", "required": True},
                {"key": "name", "label": "Product name", "type": "text", "required": True},
                {"key": "unit", "label": "Unit", "type": "text", "required": True},
                {"key": "selling_price", "label": "Selling price", "type": "money", "required": True},
            ],
        },
        {
            "key": "sales", "name": "Sales", "description": "Sales totals and payment breakdowns.",
            "fields": [
                {"key": "date", "label": "Business date", "type": "date", "required": True},
                {"key": "sku", "label": "Product code", "type": "text", "required": False},
                {"key": "quantity", "label": "Quantity sold", "type": "number", "required": True},
                {"key": "amount", "label": "Sales amount", "type": "money", "required": True},
                {"key": "payment_method", "label": "Payment method", "type": "select", "required": True, "options": ["cash", "transfer", "card", "other"]},
            ],
        },
        {
            "key": "supplier_orders", "name": "Supplier Orders", "description": "Orders placed with suppliers.",
            "fields": [
                {"key": "order_date", "label": "Order date", "type": "date", "required": True},
                {"key": "supplier", "label": "Supplier", "type": "text", "required": True},
                {"key": "reference", "label": "Order reference", "type": "text", "required": False},
                {"key": "expected_amount", "label": "Expected amount", "type": "money", "required": True},
            ],
        },
        {
            "key": "deliveries", "name": "Deliveries", "description": "Goods received against supplier orders.",
            "fields": [
                {"key": "date", "label": "Delivery date", "type": "date", "required": True},
                {"key": "supplier", "label": "Supplier", "type": "text", "required": True},
                {"key": "item", "label": "Product", "type": "text", "required": True},
                {"key": "quantity_received", "label": "Quantity received", "type": "number", "required": True},
            ],
        },
        {
            "key": "returns", "name": "Returns", "description": "Customer returns and their stock or payment impact.",
            "fields": [
                {"key": "date", "label": "Return date", "type": "date", "required": True},
                {"key": "product", "label": "Product", "type": "text", "required": True},
                {"key": "quantity", "label": "Quantity", "type": "number", "required": True},
                {"key": "reason", "label": "Reason", "type": "text", "required": True},
            ],
        },
        {
            "key": "stock_counts", "name": "Stock Counts", "description": "Physical counts used to compare expected and actual stock.",
            "fields": [
                {"key": "date", "label": "Count date", "type": "date", "required": True},
                {"key": "product", "label": "Product", "type": "text", "required": True},
                {"key": "expected_quantity", "label": "Expected quantity", "type": "number", "required": True},
                {"key": "counted_quantity", "label": "Counted quantity", "type": "number", "required": True},
            ],
        },
        {
            "key": "expenses", "name": "Expenses", "description": "Operating costs such as utilities, rent, and transport.",
            "fields": [
                {"key": "date", "label": "Date", "type": "date", "required": True},
                {"key": "category", "label": "Category", "type": "text", "required": True},
                {"key": "amount", "label": "Amount", "type": "money", "required": True},
                {"key": "description", "label": "Description", "type": "text", "required": False},
            ],
        },
        {
            "key": "supplier_payments", "name": "Supplier Payments", "description": "Payments made to suppliers and their references.",
            "fields": [
                {"key": "date", "label": "Payment date", "type": "date", "required": True},
                {"key": "supplier", "label": "Supplier", "type": "text", "required": True},
                {"key": "amount", "label": "Amount paid", "type": "money", "required": True},
                {"key": "reference", "label": "Payment reference", "type": "text", "required": False},
            ],
        },
    ],
    "trucking": [
        {
            "key": "trips", "name": "Trip Register", "description": "Trip bookings, delivery progress, fares, and customer balances.",
            "fields": [
                {"key": "date", "label": "Trip date", "type": "date", "required": True},
                {"key": "reference", "label": "Trip reference", "type": "text", "required": True},
                {"key": "customer", "label": "Customer", "type": "text", "required": True},
                {"key": "driver", "label": "Driver", "type": "text", "required": True},
                {"key": "truck_registration", "label": "Truck registration", "type": "text", "required": True},
                {"key": "pickup_location", "label": "Pickup location", "type": "text", "required": True},
                {"key": "delivery_location", "label": "Delivery location", "type": "text", "required": True},
                {"key": "cargo_description", "label": "Cargo description", "type": "text", "required": True},
                {"key": "departure_date", "label": "Departure date", "type": "date", "required": False},
                {"key": "delivery_date", "label": "Delivery date", "type": "date", "required": False},
                {"key": "trip_status", "label": "Trip status", "type": "select", "required": True, "options": ["planned", "in_transit", "delivered", "cancelled"]},
                {"key": "amount", "label": "Agreed trip fare", "type": "money", "required": True},
                {"key": "amount_paid", "label": "Amount received", "type": "money", "required": True},
                {"key": "payment_method", "label": "Payment method", "type": "select", "required": True, "options": ["cash", "transfer", "card", "credit", "other"]},
                {"key": "payment_status", "label": "Payment status", "type": "select", "required": True, "options": ["unpaid", "partially_paid", "paid"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "fleet", "name": "Truck Fleet", "description": "Vehicle register, assignment, mileage, and compliance dates.",
            "fields": [
                {"key": "date", "label": "Record date", "type": "date", "required": True},
                {"key": "reference", "label": "Vehicle reference", "type": "text", "required": True},
                {"key": "truck_registration", "label": "Truck registration", "type": "text", "required": True},
                {"key": "make_model", "label": "Make and model", "type": "text", "required": True},
                {"key": "year", "label": "Year", "type": "number", "required": False},
                {"key": "assigned_driver", "label": "Assigned driver", "type": "text", "required": False},
                {"key": "current_mileage", "label": "Current mileage (km)", "type": "number", "required": False},
                {"key": "insurance_expiry", "label": "Insurance expiry", "type": "date", "required": False},
                {"key": "roadworthiness_expiry", "label": "Roadworthiness expiry", "type": "date", "required": False},
                {"key": "vehicle_status", "label": "Vehicle status", "type": "select", "required": True, "options": ["active", "maintenance", "out_of_service", "retired"]},
                {"key": "amount", "label": "Purchase or recorded value", "type": "money", "required": False},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "trip_expenses", "name": "Trip Expenses", "description": "Costs linked to a trip, including fuel, tolls, loading, and driver allowances.",
            "fields": [
                {"key": "date", "label": "Expense date", "type": "date", "required": True},
                {"key": "reference", "label": "Expense reference", "type": "text", "required": False},
                {"key": "trip_reference", "label": "Trip reference", "type": "text", "required": True},
                {"key": "truck_registration", "label": "Truck registration", "type": "text", "required": True},
                {"key": "category", "label": "Expense category", "type": "select", "required": True, "options": ["fuel", "tolls", "loading_unloading", "driver_allowance", "accommodation", "parking", "commission", "permits", "other"]},
                {"key": "supplier_or_payee", "label": "Supplier or payee", "type": "text", "required": True},
                {"key": "amount", "label": "Expense amount", "type": "money", "required": True},
                {"key": "payment_method", "label": "Payment method", "type": "select", "required": True, "options": ["cash", "transfer", "card", "credit", "other"]},
                {"key": "payment_status", "label": "Payment status", "type": "select", "required": True, "options": ["unpaid", "partially_paid", "paid"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "payments", "name": "Money In and Out", "description": "Customer receipts, supplier payments, advances, and other cash movements.",
            "fields": [
                {"key": "date", "label": "Transaction date", "type": "date", "required": True},
                {"key": "reference", "label": "Transaction reference", "type": "text", "required": False},
                {"key": "direction", "label": "Money movement", "type": "select", "required": True, "options": ["money_in", "money_out"]},
                {"key": "party_name", "label": "Customer, supplier, or payee", "type": "text", "required": True},
                {"key": "what_for", "label": "What the payment is for", "type": "text", "required": True},
                {"key": "trip_reference", "label": "Related trip reference", "type": "text", "required": False},
                {"key": "amount", "label": "Amount", "type": "money", "required": True},
                {"key": "payment_method", "label": "Payment method", "type": "select", "required": True, "options": ["cash", "transfer", "card", "other"]},
                {"key": "payment_status", "label": "Payment status", "type": "select", "required": True, "options": ["paid", "owing", "partially_paid"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "maintenance", "name": "Service and Maintenance", "description": "Scheduled servicing, repairs, parts, and vehicle downtime.",
            "fields": [
                {"key": "date", "label": "Service or repair date", "type": "date", "required": True},
                {"key": "reference", "label": "Service reference", "type": "text", "required": False},
                {"key": "truck_registration", "label": "Truck registration", "type": "text", "required": True},
                {"key": "service_type", "label": "Service type", "type": "select", "required": True, "options": ["routine_service", "repair", "tyres", "inspection", "other"]},
                {"key": "service_provider", "label": "Mechanic or service provider", "type": "text", "required": True},
                {"key": "current_mileage", "label": "Mileage at service (km)", "type": "number", "required": False},
                {"key": "next_service_date", "label": "Next service date", "type": "date", "required": False},
                {"key": "parts_replaced", "label": "Parts replaced", "type": "text", "required": False},
                {"key": "amount", "label": "Service cost", "type": "money", "required": True},
                {"key": "payment_status", "label": "Payment status", "type": "select", "required": True, "options": ["unpaid", "partially_paid", "paid"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
        {
            "key": "drivers", "name": "Drivers and Staff", "description": "Driver details, licence dates, salary, allowances, and advances.",
            "fields": [
                {"key": "date", "label": "Record date", "type": "date", "required": True},
                {"key": "reference", "label": "Driver or staff reference", "type": "text", "required": False},
                {"key": "full_name", "label": "Full name", "type": "text", "required": True},
                {"key": "phone", "label": "Phone number", "type": "text", "required": False},
                {"key": "licence_number", "label": "Driver licence number", "type": "text", "required": False},
                {"key": "licence_expiry", "label": "Licence expiry date", "type": "date", "required": False},
                {"key": "pay_type", "label": "Pay type", "type": "select", "required": True, "options": ["salary", "per_trip", "commission", "casual"]},
                {"key": "amount", "label": "Salary, allowance, or advance", "type": "money", "required": False},
                {"key": "payment_status", "label": "Payment status", "type": "select", "required": False, "options": ["unpaid", "partially_paid", "paid"]},
                {"key": "notes", "label": "Notes", "type": "text", "required": False},
            ],
        },
    ],

    "contractor": [
        {"key":"projects","name":"Projects and Jobs","description":"Track contracts, job progress, client balances, and completion.","fields":[{"key":"date","label":"Start date","type":"date","required":True},{"key":"reference","label":"Job reference","type":"text","required":True},{"key":"client","label":"Client","type":"text","required":True},{"key":"project_name","label":"Project or job","type":"text","required":True},{"key":"location","label":"Site location","type":"text","required":False},{"key":"status","label":"Job status","type":"select","required":True,"options":["quoted","active","on_hold","completed","cancelled"]},{"key":"contract_amount","label":"Contract amount","type":"money","required":True},{"key":"amount_paid","label":"Amount received","type":"money","required":True},{"key":"due_date","label":"Target completion","type":"date","required":False},{"key":"notes","label":"Notes","type":"text","required":False}]},
        {"key":"job_costs","name":"Job Costs","description":"Materials, labour, equipment hire, and other job costs.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"job_reference","label":"Job reference","type":"text","required":True},{"key":"category","label":"Cost category","type":"select","required":True,"options":["materials","labour","equipment","transport","subcontractor","other"]},{"key":"supplier_or_payee","label":"Supplier or payee","type":"text","required":True},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"payment_status","label":"Payment status","type":"select","required":True,"options":["paid","owing","partially_paid"]},{"key":"notes","label":"Notes","type":"text","required":False}]},
        {"key":"quotes_invoices","name":"Quotes and Invoices","description":"Track estimates, invoices, due dates, and collections.","fields":[{"key":"date","label":"Issue date","type":"date","required":True},{"key":"reference","label":"Quote or invoice number","type":"text","required":True},{"key":"client","label":"Client","type":"text","required":True},{"key":"job_reference","label":"Job reference","type":"text","required":False},{"key":"document_type","label":"Document type","type":"select","required":True,"options":["quote","invoice","variation"]},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"due_date","label":"Due date","type":"date","required":False},{"key":"status","label":"Status","type":"select","required":True,"options":["draft","sent","accepted","paid","overdue","cancelled"]}]},
    ],
    "hotel": [
        {"key":"reservations","name":"Bookings and Reservations","description":"Guest bookings, room allocation, stay dates, and payment status.","fields":[{"key":"date","label":"Booking date","type":"date","required":True},{"key":"reference","label":"Booking reference","type":"text","required":True},{"key":"guest_name","label":"Guest name","type":"text","required":True},{"key":"room_number","label":"Room number","type":"text","required":True},{"key":"check_in","label":"Check-in","type":"date","required":True},{"key":"check_out","label":"Check-out","type":"date","required":True},{"key":"booking_status","label":"Booking status","type":"select","required":True,"options":["reserved","checked_in","checked_out","cancelled","no_show"]},{"key":"amount","label":"Booking total","type":"money","required":True},{"key":"amount_paid","label":"Amount paid","type":"money","required":True}]},
        {"key":"room_register","name":"Rooms and Housekeeping","description":"Room status, cleaning, and maintenance readiness.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"room_number","label":"Room number","type":"text","required":True},{"key":"room_type","label":"Room type","type":"text","required":True},{"key":"status","label":"Room status","type":"select","required":True,"options":["available","occupied","needs_cleaning","maintenance","out_of_service"]},{"key":"last_cleaned","label":"Last cleaned","type":"date","required":False},{"key":"notes","label":"Notes","type":"text","required":False}]},
        {"key":"hotel_expenses","name":"Hotel Expenses","description":"Utilities, supplies, laundry, repairs, and operating costs.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"category","label":"Expense category","type":"text","required":True},{"key":"supplier","label":"Supplier or payee","type":"text","required":False},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"payment_status","label":"Payment status","type":"select","required":True,"options":["paid","owing","partially_paid"]}]},
    ],
    "farm": [
        {"key":"farm_overview","name":"Farm Operations","description":"Shared farm register for land, season, general activity, and operating notes.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"reference","label":"Activity reference","type":"text","required":False},{"key":"farm_unit","label":"Farm or plot","type":"text","required":True},{"key":"season","label":"Season or cycle","type":"text","required":False},{"key":"activity","label":"Activity","type":"text","required":True},{"key":"area_or_quantity","label":"Area or quantity","type":"number","required":False},{"key":"unit","label":"Unit","type":"text","required":False},{"key":"amount","label":"Cost or income","type":"money","required":False},{"key":"notes","label":"Notes","type":"text","required":False}]},
        {"key":"farm_cashbook","name":"Farm Money In and Out","description":"Shared farm income, spending, wages, and supplier payments.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"direction","label":"Direction","type":"select","required":True,"options":["money_in","money_out"]},{"key":"category","label":"Category","type":"text","required":True},{"key":"party","label":"Customer, supplier, or worker","type":"text","required":False},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"payment_method","label":"Payment method","type":"select","required":True,"options":["cash","transfer","card","other"]},{"key":"notes","label":"Notes","type":"text","required":False}]},
    ],
    "rental_property": [
        {"key":"properties","name":"Property Register","description":"Units, ownership references, rent terms, and occupancy.","fields":[{"key":"date","label":"Record date","type":"date","required":True},{"key":"property_reference","label":"Property or unit reference","type":"text","required":True},{"key":"address","label":"Property address","type":"text","required":True},{"key":"property_type","label":"Property type","type":"text","required":True},{"key":"rent_amount","label":"Rent amount","type":"money","required":True},{"key":"rent_frequency","label":"Rent frequency","type":"select","required":True,"options":["monthly","quarterly","yearly","other"]},{"key":"occupancy","label":"Occupancy","type":"select","required":True,"options":["occupied","vacant","maintenance"]}]},
        {"key":"tenants_rent","name":"Tenants and Rent Payments","description":"Tenant contacts, lease dates, rent due, and outstanding balances.","fields":[{"key":"date","label":"Entry date","type":"date","required":True},{"key":"tenant_name","label":"Tenant name","type":"text","required":True},{"key":"property_reference","label":"Property or unit","type":"text","required":True},{"key":"lease_start","label":"Lease start","type":"date","required":False},{"key":"lease_end","label":"Lease end","type":"date","required":False},{"key":"rent_due","label":"Rent due","type":"money","required":True},{"key":"amount_paid","label":"Amount paid","type":"money","required":True},{"key":"next_due_date","label":"Next due date","type":"date","required":False}]},
        {"key":"property_maintenance","name":"Property Maintenance","description":"Repairs, inspections, contractor work, and vacancy-related costs.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"property_reference","label":"Property or unit","type":"text","required":True},{"key":"issue","label":"Issue or work","type":"text","required":True},{"key":"contractor","label":"Contractor","type":"text","required":False},{"key":"amount","label":"Cost","type":"money","required":True},{"key":"status","label":"Status","type":"select","required":True,"options":["reported","scheduled","in_progress","completed"]}]},
    ],
    "school": [
        {"key":"students","name":"Student Register","description":"Student identifiers, class, guardian contact, and enrolment status.","fields":[{"key":"date","label":"Enrolment date","type":"date","required":True},{"key":"student_reference","label":"Student ID","type":"text","required":True},{"key":"student_name","label":"Student name","type":"text","required":True},{"key":"class_level","label":"Class or level","type":"text","required":True},{"key":"guardian_name","label":"Guardian name","type":"text","required":False},{"key":"guardian_phone","label":"Guardian phone","type":"text","required":False},{"key":"status","label":"Enrolment status","type":"select","required":True,"options":["active","graduated","withdrawn"]}]},
        {"key":"school_fees","name":"School Fees and Balances","description":"Fees charged, payments received, and outstanding balances by student.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"student_reference","label":"Student ID","type":"text","required":True},{"key":"student_name","label":"Student name","type":"text","required":True},{"key":"term","label":"Term or session","type":"text","required":True},{"key":"fee_type","label":"Fee type","type":"text","required":True},{"key":"amount_due","label":"Amount due","type":"money","required":True},{"key":"amount_paid","label":"Amount paid","type":"money","required":True},{"key":"due_date","label":"Due date","type":"date","required":False}]},
        {"key":"attendance","name":"Attendance Register","description":"Daily attendance counts or individual attendance entries.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"student_reference","label":"Student ID","type":"text","required":False},{"key":"student_name","label":"Student name","type":"text","required":False},{"key":"class_level","label":"Class or level","type":"text","required":True},{"key":"attendance_status","label":"Attendance","type":"select","required":True,"options":["present","absent","late","excused"]}]},
    ],
    "salon": [
        {"key":"appointments","name":"Appointments and Services","description":"Bookings, service types, staff, and customer payments.","fields":[{"key":"date","label":"Appointment date","type":"date","required":True},{"key":"customer","label":"Customer","type":"text","required":True},{"key":"service","label":"Service","type":"text","required":True},{"key":"staff_member","label":"Staff member","type":"text","required":False},{"key":"status","label":"Appointment status","type":"select","required":True,"options":["booked","completed","cancelled","no_show"]},{"key":"amount","label":"Service amount","type":"money","required":True},{"key":"amount_paid","label":"Amount paid","type":"money","required":True},{"key":"payment_method","label":"Payment method","type":"select","required":True,"options":["cash","transfer","card","other"]}]},
        {"key":"salon_stock","name":"Products and Supplies","description":"Beauty products, consumables, and stock purchases or usage.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"item","label":"Product or supply","type":"text","required":True},{"key":"movement","label":"Movement","type":"select","required":True,"options":["purchased","used","sold","adjustment"]},{"key":"quantity","label":"Quantity","type":"number","required":True},{"key":"amount","label":"Cost or sale value","type":"money","required":False}]},
        {"key":"salon_expenses","name":"Expenses and Staff Payments","description":"Rent, utilities, supplies, commissions, and wages.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"category","label":"Category","type":"text","required":True},{"key":"payee","label":"Payee","type":"text","required":False},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"notes","label":"Notes","type":"text","required":False}]},
    ],
    "training": [
        {"key":"courses","name":"Courses and Cohorts","description":"Course catalogue, batches, dates, and pricing.","fields":[{"key":"date","label":"Start date","type":"date","required":True},{"key":"course_reference","label":"Course or cohort ID","type":"text","required":True},{"key":"course_name","label":"Course name","type":"text","required":True},{"key":"trainer","label":"Trainer","type":"text","required":False},{"key":"start_date","label":"Start date","type":"date","required":False},{"key":"end_date","label":"End date","type":"date","required":False},{"key":"fee","label":"Course fee","type":"money","required":True},{"key":"status","label":"Status","type":"select","required":True,"options":["planned","enrolling","in_progress","completed","cancelled"]}]},
        {"key":"learners_payments","name":"Learners and Payments","description":"Learner enrolments, fee payments, and outstanding balances.","fields":[{"key":"date","label":"Enrolment date","type":"date","required":True},{"key":"learner_name","label":"Learner name","type":"text","required":True},{"key":"course_reference","label":"Course or cohort ID","type":"text","required":True},{"key":"contact","label":"Contact","type":"text","required":False},{"key":"amount_due","label":"Amount due","type":"money","required":True},{"key":"amount_paid","label":"Amount paid","type":"money","required":True},{"key":"status","label":"Learner status","type":"select","required":True,"options":["enrolled","completed","withdrawn"]}]},
        {"key":"training_expenses","name":"Training Expenses","description":"Venue, materials, internet, equipment, and trainer costs.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"category","label":"Category","type":"text","required":True},{"key":"supplier_or_payee","label":"Supplier or payee","type":"text","required":False},{"key":"amount","label":"Amount","type":"money","required":True},{"key":"notes","label":"Notes","type":"text","required":False}]},
    ],
    "pharmacy": [
        {"key":"medicine_stock","name":"Medicine and Product Stock","description":"Product batches, expiry dates, stock levels, and purchase costs.","fields":[{"key":"date","label":"Record date","type":"date","required":True},{"key":"product_code","label":"Product code","type":"text","required":True},{"key":"product_name","label":"Medicine or product name","type":"text","required":True},{"key":"batch_number","label":"Batch number","type":"text","required":False},{"key":"expiry_date","label":"Expiry date","type":"date","required":False},{"key":"quantity","label":"Quantity on hand","type":"number","required":True},{"key":"unit_cost","label":"Unit cost","type":"money","required":False},{"key":"selling_price","label":"Selling price","type":"money","required":True}]},
        {"key":"pharmacy_sales","name":"Sales and Dispensing Log","description":"Product sales and dispensing transaction records. Do not use this as a clinical record.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"receipt_reference","label":"Receipt reference","type":"text","required":False},{"key":"product_name","label":"Product name","type":"text","required":True},{"key":"quantity","label":"Quantity sold","type":"number","required":True},{"key":"amount","label":"Total sale","type":"money","required":True},{"key":"payment_method","label":"Payment method","type":"select","required":True,"options":["cash","transfer","card","other"]}]},
        {"key":"pharmacy_purchases","name":"Supplier Purchases and Expiry Checks","description":"Supplier invoices, purchases, and stock expiry review.","fields":[{"key":"date","label":"Purchase date","type":"date","required":True},{"key":"supplier","label":"Supplier","type":"text","required":True},{"key":"invoice_reference","label":"Invoice reference","type":"text","required":False},{"key":"product_name","label":"Product name","type":"text","required":True},{"key":"quantity","label":"Quantity purchased","type":"number","required":True},{"key":"amount","label":"Purchase total","type":"money","required":True},{"key":"expiry_date","label":"Expiry date","type":"date","required":False}]},
    ],

}


FARM_MODULE_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "crops": [
        {"key":"crop_cycles","name":"Crop Planting and Harvests","description":"Crop, plot, planting, harvest, and yield records.","fields":[{"key":"date","label":"Activity date","type":"date","required":True},{"key":"crop","label":"Crop","type":"text","required":True},{"key":"plot","label":"Plot or field","type":"text","required":True},{"key":"activity","label":"Activity","type":"select","required":True,"options":["land_preparation","planting","weeding","fertilising","spraying","harvest"]},{"key":"quantity","label":"Harvest quantity","type":"number","required":False},{"key":"amount","label":"Cost or sales value","type":"money","required":False}]},
        {"key":"crop_inputs","name":"Seeds, Fertiliser and Crop Inputs","description":"Input purchases and application by plot or crop cycle.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"crop","label":"Crop","type":"text","required":True},{"key":"input_name","label":"Input","type":"text","required":True},{"key":"quantity","label":"Quantity","type":"number","required":True},{"key":"supplier","label":"Supplier","type":"text","required":False},{"key":"amount","label":"Cost","type":"money","required":True}]},
    ],
    "livestock": [
        {"key":"livestock_register","name":"Livestock Register","description":"Animal groups, head counts, births, purchases, sales, and losses.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"animal_type","label":"Animal type","type":"text","required":True},{"key":"movement","label":"Movement","type":"select","required":True,"options":["opening_count","birth","purchase","sale","death","transfer"]},{"key":"head_count","label":"Number of animals","type":"number","required":True},{"key":"amount","label":"Cost or sales value","type":"money","required":False}]},
        {"key":"livestock_health_feed","name":"Feed and Animal Care","description":"Feed, vaccinations, veterinary costs, and care activities.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"animal_group","label":"Animal group or tag","type":"text","required":True},{"key":"activity","label":"Care activity","type":"select","required":True,"options":["feed","vaccination","treatment","vet_visit","other"]},{"key":"amount","label":"Cost","type":"money","required":False}]},
    ],
    "poultry": [
        {"key":"flock_register","name":"Flock and Batch Register","description":"Poultry batches, bird counts, placement dates, and mortality.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"batch_reference","label":"Batch reference","type":"text","required":True},{"key":"bird_type","label":"Bird type","type":"select","required":True,"options":["broiler","layer","cockerel","other"]},{"key":"birds_added","label":"Birds added","type":"number","required":False},{"key":"mortality","label":"Mortality count","type":"number","required":False},{"key":"birds_sold","label":"Birds sold","type":"number","required":False}]},
        {"key":"poultry_feed_eggs","name":"Feed, Eggs and Poultry Output","description":"Feed consumption, egg production, and batch output.","fields":[{"key":"date","label":"Date","type":"date","required":True},{"key":"batch_reference","label":"Batch reference","type":"text","required":True},{"key":"activity","label":"Activity","type":"select","required":True,"options":["feed_received","feed_used","eggs_collected","birds_sold","other_output"]},{"key":"quantity","label":"Quantity","type":"number","required":True},{"key":"unit","label":"Unit","type":"text","required":True}]},
    ],
}

def templates_for(business_type: str, farm_modules: list[str] | None = None) -> list[dict[str, Any]]:
    """Return fresh starter templates; farm modules are opt-in per workspace."""
    import copy
    templates = copy.deepcopy(TEMPLATE_DEFINITIONS[business_type])
    if business_type == "farm":
        for module in ("crops", "livestock", "poultry"):
            if module in (farm_modules or []):
                templates.extend(copy.deepcopy(FARM_MODULE_TEMPLATES[module]))
    return templates
