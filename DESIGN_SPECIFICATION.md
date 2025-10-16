# Design Specification
## Coffee Ordering System

### 1. Conceptual Data Model - E-R Diagram and Business Rules

#### 1.1 Entity-Relationship Diagram

```
                    CUSTOMER
                ┌─────────────────┐
                │ CUSTOMER_ID (PK)│
                │ NAME            │
                │ PHONE           │
                │ EMAIL           │
                │ ADDRESS         │
                │ CUSTOMER_TYPE   │
                └─────────────────┘
                         │
                         │ 1:N
                         │
                    MEMBER_CUSTOMERS
                ┌─────────────────┐
                │ CUSTOMER_ID (PK)│
                │ PASSWORD_HASH   │
                │ DATE_OF_BIRTH   │
                │ REGISTRATION_DATE│
                └─────────────────┘

                    CATEGORY
                ┌─────────────────┐
                │ CATEGORY_ID (PK)│
                │ CATEGORY_NAME   │
                │ DESCRIPTION     │
                └─────────────────┘
                         │
                         │ 1:N
                         │
                    PRODUCT
                ┌─────────────────┐
                │ PRODUCT_ID (PK) │
                │ NAME            │
                │ PRICE           │
                │ IS_ACTIVE       │
                │ CATEGORY_ID (FK)│
                └─────────────────┘
                         │
                         │ 1:N
                         │
                    ORDERS
                ┌─────────────────┐
                │ ORDER_ID (PK)   │
                │ CUSTOMER_ID (FK)│
                │ ORDER_DATE      │
                │ STATUS          │
                │ PAYMENT_METHOD  │
                │ TOTAL_AMOUNT    │
                └─────────────────┘
                         │
                         │ 1:N
                         │
                    ORDER_ITEMS
                ┌─────────────────┐
                │ ORDER_ITEM_ID (PK)│
                │ ORDER_ID (FK)   │
                │ PRODUCT_ID (FK) │
                │ QUANTITY        │
                │ UNIT_PRICE      │
                │ LINE_AMOUNT     │
                └─────────────────┘
```

#### 1.2 Business Rules and Constraints

**Customer Management Rules:**
1. Every customer must have a unique CUSTOMER_ID
2. Customer names are required and cannot be null
3. Email addresses must be unique for members
4. Customer types are limited to 'regular' and 'member'
5. Members must have associated records in MEMBER_CUSTOMERS table

**Product Management Rules:**
1. Every product must belong to exactly one category
2. Product prices must be positive decimal values
3. Product names must be unique within the system
4. Only active products (IS_ACTIVE = 'Y') can be ordered
5. Categories cannot be deleted if they contain active products

**Order Management Rules:**
1. Every order must be associated with exactly one customer
2. Orders must contain at least one order item
3. Order total amount must equal the sum of all line amounts
4. Order status must be one of: 'pending', 'processing', 'completed', 'cancelled'
5. Payment methods are limited to: 'cash', 'card', 'alipay', 'wechat'

**Member-Specific Rules:**
1. Members must provide a password during registration
2. Member passwords are stored as hashed values, never in plain text
3. Members can view their own order history
4. Member registration date is automatically set to current timestamp

**Data Integrity Rules:**
1. Foreign key relationships must be maintained
2. Cascade delete is not allowed for customer records with orders
3. Order items cannot be modified after order completion
4. Product prices in order items are frozen at time of order creation

### 2. Logical Data Model - Relational Schema

#### 2.1 Normalization Process

**First Normal Form (1NF):**
- All tables have atomic values
- No repeating groups
- Each row is unique

**Second Normal Form (2NF):**
- All non-key attributes are fully dependent on the primary key
- No partial dependencies

**Third Normal Form (3NF):**
- No transitive dependencies
- All non-key attributes depend only on the primary key

#### 2.2 Functional Dependencies

**CUSTOMER Table:**
- CUSTOMER_ID → NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE

**MEMBER_CUSTOMERS Table:**
- CUSTOMER_ID → PASSWORD_HASH, DATE_OF_BIRTH, REGISTRATION_DATE

**CATEGORY Table:**
- CATEGORY_ID → CATEGORY_NAME, DESCRIPTION

**PRODUCT Table:**
- PRODUCT_ID → NAME, PRICE, IS_ACTIVE, CATEGORY_ID
- CATEGORY_ID → CATEGORY_NAME (transitive dependency resolved by separate table)

**ORDERS Table:**
- ORDER_ID → CUSTOMER_ID, ORDER_DATE, STATUS, PAYMENT_METHOD, TOTAL_AMOUNT
- CUSTOMER_ID → NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE (transitive dependency resolved)

**ORDER_ITEMS Table:**
- ORDER_ITEM_ID → ORDER_ID, PRODUCT_ID, QUANTITY, UNIT_PRICE, LINE_AMOUNT
- ORDER_ID → CUSTOMER_ID, ORDER_DATE, STATUS, PAYMENT_METHOD, TOTAL_AMOUNT (transitive dependency resolved)
- PRODUCT_ID → NAME, PRICE, IS_ACTIVE, CATEGORY_ID (transitive dependency resolved)

#### 2.3 Normalization Status
All tables are in **Third Normal Form (3NF)**:
- No partial dependencies
- No transitive dependencies
- All non-key attributes depend only on the primary key

### 3. Data Dictionary

#### 3.1 CUSTOMER Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| CUSTOMER_ID | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each customer |
| NAME | VARCHAR(100) | NOT NULL | Customer's full name |
| PHONE | VARCHAR(30) | NULL | Customer's phone number |
| EMAIL | VARCHAR(120) | NULL | Customer's email address |
| ADDRESS | VARCHAR(255) | NULL | Customer's address |
| CUSTOMER_TYPE | VARCHAR(10) | DEFAULT 'regular' | Type: 'regular' or 'member' |

#### 3.2 MEMBER_CUSTOMERS Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| CUSTOMER_ID | INTEGER | PRIMARY KEY, FOREIGN KEY | References CUSTOMER.CUSTOMER_ID |
| PASSWORD_HASH | VARCHAR(255) | NOT NULL | Hashed password for member login |
| DATE_OF_BIRTH | DATE | NULL | Member's date of birth |
| REGISTRATION_DATE | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When member registered |

#### 3.3 CATEGORY Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| CATEGORY_ID | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each category |
| CATEGORY_NAME | VARCHAR(80) | UNIQUE, NOT NULL | Name of the category |
| DESCRIPTION | VARCHAR(255) | NULL | Description of the category |

#### 3.4 PRODUCT Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| PRODUCT_ID | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each product |
| NAME | VARCHAR(120) | NOT NULL | Product name |
| PRICE | DECIMAL(10,2) | NOT NULL | Product price |
| IS_ACTIVE | CHAR(1) | DEFAULT 'Y' | Active status: 'Y' or 'N' |
| CATEGORY_ID | INTEGER | FOREIGN KEY | References CATEGORY.CATEGORY_ID |

#### 3.5 ORDERS Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| ORDER_ID | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each order |
| CUSTOMER_ID | INTEGER | FOREIGN KEY | References CUSTOMER.CUSTOMER_ID |
| ORDER_DATE | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When order was placed |
| STATUS | VARCHAR(20) | DEFAULT 'pending' | Order status |
| PAYMENT_METHOD | VARCHAR(20) | NULL | Payment method used |
| TOTAL_AMOUNT | DECIMAL(12,2) | NULL | Total amount of the order |

#### 3.6 ORDER_ITEMS Table
| Attribute | Data Type | Constraints | Description |
|-----------|-----------|-------------|-------------|
| ORDER_ITEM_ID | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each order item |
| ORDER_ID | INTEGER | FOREIGN KEY | References ORDERS.ORDER_ID |
| PRODUCT_ID | INTEGER | FOREIGN KEY | References PRODUCT.PRODUCT_ID |
| QUANTITY | INTEGER(10) | NULL | Quantity ordered |
| UNIT_PRICE | DECIMAL(10,2) | NULL | Price per unit at time of order |
| LINE_AMOUNT | DECIMAL(10,2) | NULL | Total amount for this line item |

#### 3.7 Relationships Summary
- **CUSTOMER** (1) ←→ (0,1) **MEMBER_CUSTOMERS**: One-to-one optional
- **CATEGORY** (1) ←→ (0,N) **PRODUCT**: One-to-many
- **CUSTOMER** (1) ←→ (0,N) **ORDERS**: One-to-many
- **ORDERS** (1) ←→ (1,N) **ORDER_ITEMS**: One-to-many
- **PRODUCT** (1) ←→ (0,N) **ORDER_ITEMS**: One-to-many
