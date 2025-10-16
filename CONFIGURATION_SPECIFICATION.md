# Configuration Specification
## SQL Statements Configurations and Specifications

### Overview
This document provides comprehensive documentation of all SQL statements used in the Coffee Ordering System database. The statements are organized by functionality and include detailed explanations of their purpose and utility to users.

### 1. Data Retrieval Queries

#### 1.1 Product Management Queries

**Query 1: Get All Active Products**
```sql
SELECT p.PRODUCT_ID, p.NAME, p.PRICE, p.IS_ACTIVE, c.CATEGORY_NAME
FROM CYEAE_PRODUCT p
LEFT JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
WHERE p.IS_ACTIVE = 'Y'
ORDER BY c.CATEGORY_NAME, p.NAME;
```
**Purpose**: Retrieves all active products with their category information for display in the menu.
**User Utility**: Customers can view the complete product catalog with prices and categories.

**Query 2: Get All Categories**
```sql
SELECT CATEGORY_ID, CATEGORY_NAME, DESCRIPTION 
FROM CYEAE_CATEGORY 
ORDER BY CATEGORY_NAME;
```
**Purpose**: Retrieves all product categories for menu organization.
**User Utility**: Enables proper categorization and filtering of products in the user interface.

#### 1.2 Customer Management Queries

**Query 3: Get Customer by ID**
```sql
SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
FROM CYEAE_CUSTOMER 
WHERE CUSTOMER_ID = ?;
```
**Purpose**: Retrieves specific customer information for order processing and profile management.
**User Utility**: Allows retrieval of customer details for order confirmation and account management.

**Query 4: Get Member by Email**
```sql
SELECT c.CUSTOMER_ID, c.NAME, c.PHONE, c.EMAIL, c.ADDRESS, c.CUSTOMER_TYPE,
       m.PASSWORD_HASH, m.DATE_OF_BIRTH, m.REGISTRATION_DATE
FROM CYEAE_CUSTOMER c
JOIN CYEAE_MEMBER_CUSTOMERS m ON c.CUSTOMER_ID = m.CUSTOMER_ID
WHERE c.EMAIL = ?;
```
**Purpose**: Authenticates member login by retrieving member information with password hash.
**User Utility**: Enables secure member authentication and profile access.

#### 1.3 Order Management Queries

**Query 5: Get Order History**
```sql
SELECT o.ORDER_ID, c.NAME, o.ORDER_DATE, o.STATUS, o.PAYMENT_METHOD, o.TOTAL_AMOUNT
FROM CYEAE_ORDERS o
JOIN CYEAE_CUSTOMER c ON o.CUSTOMER_ID = c.CUSTOMER_ID
WHERE o.CUSTOMER_ID = ?
ORDER BY o.ORDER_DATE DESC;
```
**Purpose**: Retrieves order history for a specific customer.
**User Utility**: Members can view their past orders and track order status.

**Query 6: Get Order Details**
```sql
SELECT oi.PRODUCT_ID, p.NAME, oi.QUANTITY, oi.UNIT_PRICE, oi.LINE_AMOUNT
FROM CYEAE_ORDER_ITEMS oi
JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
WHERE oi.ORDER_ID = ?;
```
**Purpose**: Retrieves detailed items for a specific order.
**User Utility**: Provides complete order breakdown including quantities and prices.

### 2. Data Insertion Queries

#### 2.1 Customer Creation

**Query 7: Create Customer**
```sql
INSERT INTO CYEAE_CUSTOMER (NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE)
VALUES (?, ?, ?, ?, ?);
```
**Purpose**: Creates new customer records for both regular and member customers.
**User Utility**: Enables customer registration and order processing for new customers.

**Query 8: Create Member Customer**
```sql
INSERT INTO CYEAE_MEMBER_CUSTOMERS (CUSTOMER_ID, PASSWORD_HASH, DATE_OF_BIRTH)
VALUES (?, ?, ?);
```
**Purpose**: Creates member-specific information including password and personal details.
**User Utility**: Enables secure member account creation with authentication credentials.

#### 2.2 Order Processing

**Query 9: Create Order**
```sql
INSERT INTO CYEAE_ORDERS (CUSTOMER_ID, PAYMENT_METHOD, TOTAL_AMOUNT)
VALUES (?, ?, ?);
```
**Purpose**: Creates new order records with customer and payment information.
**User Utility**: Processes customer orders and initiates the order fulfillment process.

**Query 10: Create Order Items**
```sql
INSERT INTO CYEAE_ORDER_ITEMS (ORDER_ID, PRODUCT_ID, QUANTITY, UNIT_PRICE, LINE_AMOUNT)
VALUES (?, ?, ?, ?, ?);
```
**Purpose**: Records individual items within an order with quantities and prices.
**User Utility**: Maintains detailed order records for fulfillment and customer service.

### 3. Reporting and Analytics Queries

#### 3.1 Sales Analysis

**Query 11: Sales Report by Date Range**
```sql
SELECT 
    DATE(o.ORDER_DATE) as order_date,
    COUNT(o.ORDER_ID) as order_count,
    SUM(o.TOTAL_AMOUNT) as total_sales,
    AVG(o.TOTAL_AMOUNT) as avg_order_value
FROM CYEAE_ORDERS o
WHERE DATE(o.ORDER_DATE) >= ? AND DATE(o.ORDER_DATE) <= ?
GROUP BY DATE(o.ORDER_DATE) 
ORDER BY order_date DESC;
```
**Purpose**: Generates daily sales reports with order counts and revenue metrics.
**User Utility**: Provides business owners with insights into daily performance and trends.

**Query 12: Product Sales Report**
```sql
SELECT 
    p.NAME as product_name,
    c.CATEGORY_NAME,
    SUM(oi.QUANTITY) as total_quantity,
    SUM(oi.LINE_AMOUNT) as total_revenue,
    COUNT(DISTINCT oi.ORDER_ID) as order_count
FROM CYEAE_ORDER_ITEMS oi
JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
GROUP BY p.PRODUCT_ID, p.NAME, c.CATEGORY_NAME
ORDER BY total_revenue DESC;
```
**Purpose**: Analyzes product performance by sales volume and revenue.
**User Utility**: Helps identify best-selling products and optimize inventory and marketing.

#### 3.2 Customer Analysis

**Query 13: Customer Report**
```sql
SELECT 
    c.NAME as customer_name,
    c.CUSTOMER_TYPE,
    COUNT(o.ORDER_ID) as order_count,
    SUM(o.TOTAL_AMOUNT) as total_spent,
    AVG(o.TOTAL_AMOUNT) as avg_order_value,
    MAX(o.ORDER_DATE) as last_order_date
FROM CYEAE_CUSTOMER c
LEFT JOIN CYEAE_ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
GROUP BY c.CUSTOMER_ID, c.NAME, c.CUSTOMER_TYPE
ORDER BY total_spent DESC;
```
**Purpose**: Provides comprehensive customer analysis including spending patterns and loyalty metrics.
**User Utility**: Enables customer segmentation and targeted marketing strategies.

### 4. Data Maintenance Queries

#### 4.1 Database Initialization

**Query 14: Initialize Categories**
```sql
INSERT INTO CYEAE_CATEGORY (CATEGORY_NAME, DESCRIPTION) VALUES 
('Coffee', 'Coffee beverages'),
('Tea', 'Tea drinks'),
('Dessert', 'Cakes and snacks'),
('Light Meal', 'Sandwiches and salads');
```
**Purpose**: Sets up initial product categories for the system.
**User Utility**: Establishes the foundation for product organization and menu structure.

**Query 15: Initialize Products**
```sql
INSERT INTO CYEAE_PRODUCT (NAME, PRICE, IS_ACTIVE, CATEGORY_ID) VALUES 
('Americano', 25.00, 'Y', 1),
('Latte', 32.00, 'Y', 1),
('Cappuccino', 30.00, 'Y', 1),
('Mocha', 35.00, 'Y', 1),
('chinesetea', 28.00, 'Y', 2),
('Milk Tea', 22.00, 'Y', 2),
('Cheesecake', 38.00, 'Y', 3),
('Tiramisu', 42.00, 'Y', 3),
('Ham Sandwich', 28.00, 'Y', 4),
('Caesar Salad', 32.00, 'Y', 4);
```
**Purpose**: Populates the system with initial product offerings.
**User Utility**: Provides customers with a complete menu of available items.

### 5. Advanced SQL Features Used

#### 5.1 Joins
- **LEFT JOIN**: Used to include products even if category information is missing
- **INNER JOIN**: Used to combine customer and member information for authentication
- **Multiple JOINs**: Used in reporting queries to combine data from multiple tables

#### 5.2 Aggregation Functions
- **COUNT()**: Used to count orders and items
- **SUM()**: Used to calculate totals and revenue
- **AVG()**: Used to calculate average order values
- **MAX()**: Used to find latest order dates

#### 5.3 Grouping and Filtering
- **GROUP BY**: Used to aggregate data by categories, dates, and customers
- **WHERE**: Used to filter data by date ranges, customer types, and status
- **ORDER BY**: Used to sort results by relevance and performance metrics

#### 5.4 Data Types and Constraints
- **DECIMAL**: Used for precise monetary calculations
- **TIMESTAMP**: Used for accurate date and time recording
- **VARCHAR**: Used for variable-length text fields
- **FOREIGN KEY**: Used to maintain referential integrity

### 6. Query Performance Considerations

#### 6.1 Indexing Strategy
- Primary keys are automatically indexed
- Foreign key columns should be indexed for join performance
- Frequently queried columns (EMAIL, ORDER_DATE) should be indexed

#### 6.2 Query Optimization
- Use specific WHERE clauses to limit result sets
- Avoid SELECT * in production queries
- Use appropriate JOIN types based on data relationships
- Consider query execution plans for complex reports

### 7. Security Considerations

#### 7.1 Parameterized Queries
All queries use parameterized statements (?) to prevent SQL injection attacks.

#### 7.2 Data Validation
- Input validation is performed at the application level
- Database constraints ensure data integrity
- Password hashing prevents plain text storage

#### 7.3 Access Control
- Admin queries require authentication
- Customer data access is restricted to authorized operations
- Sensitive information (passwords) is properly hashed
