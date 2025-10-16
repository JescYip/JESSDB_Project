import sqlite3
import hashlib
from datetime import datetime, date

class DatabaseManager:
    def __init__(self, db_path='coffee_shop.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_CUSTOMER (
                CUSTOMER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME VARCHAR(100) NOT NULL,
                PHONE VARCHAR(30),
                EMAIL VARCHAR(120),
                ADDRESS VARCHAR(255),
                CUSTOMER_TYPE VARCHAR(10) DEFAULT 'regular'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_MEMBER_CUSTOMERS (
                CUSTOMER_ID INTEGER PRIMARY KEY,
                PASSWORD_HASH VARCHAR(255) NOT NULL,
                DATE_OF_BIRTH DATE,
                REGISTRATION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (CUSTOMER_ID) REFERENCES CYEAE_CUSTOMER(CUSTOMER_ID)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_CATEGORY (
                CATEGORY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CATEGORY_NAME VARCHAR(80) UNIQUE NOT NULL,
                DESCRIPTION VARCHAR(255)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_PRODUCT (
                PRODUCT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME VARCHAR(120) NOT NULL,
                PRICE DECIMAL(10,2) NOT NULL,
                IS_ACTIVE CHAR(1) DEFAULT 'Y',
                CATEGORY_ID INTEGER,
                FOREIGN KEY (CATEGORY_ID) REFERENCES CYEAE_CATEGORY(CATEGORY_ID)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_ORDERS (
                ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CUSTOMER_ID INTEGER,
                ORDER_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                STATUS VARCHAR(20) DEFAULT 'pending',
                PAYMENT_METHOD VARCHAR(20),
                TOTAL_AMOUNT DECIMAL(12,2),
                FOREIGN KEY (CUSTOMER_ID) REFERENCES CYEAE_CUSTOMER(CUSTOMER_ID)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CYEAE_ORDER_ITEMS (
                ORDER_ITEM_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ORDER_ID INTEGER,
                PRODUCT_ID INTEGER,
                QUANTITY INTEGER(10),
                UNIT_PRICE DECIMAL(10,2),
                LINE_AMOUNT DECIMAL(10,2),
                FOREIGN KEY (ORDER_ID) REFERENCES CYEAE_ORDERS(ORDER_ID),
                FOREIGN KEY (PRODUCT_ID) REFERENCES CYEAE_PRODUCT(PRODUCT_ID)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.insert_sample_data()
    
    def insert_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM CYEAE_CATEGORY")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        categories = [
            ('Coffee', 'Coffee beverages'),
            ('Tea', 'Tea drinks'),
            ('Dessert', 'Cakes and snacks'),
            ('Light Meal', 'Sandwiches and salads')
        ]
        cursor.executemany("INSERT INTO CYEAE_CATEGORY (CATEGORY_NAME, DESCRIPTION) VALUES (?, ?)", categories)
        
        products = [
            ('Americano', 25.00, 'Y', 1),
            ('Latte', 32.00, 'Y', 1),
            ('Cappuccino', 30.00, 'Y', 1),
            ('Mocha', 35.00, 'Y', 1),
            ('chinesetea', 28.00, 'Y', 2),
            ('Milk Tea', 22.00, 'Y', 2),
            ('Cheesecake', 38.00, 'Y', 3),
            ('Tiramisu', 42.00, 'Y', 3),
            ('Ham Sandwich', 28.00, 'Y', 4),
            ('Caesar Salad', 32.00, 'Y', 4)
        ]
        cursor.executemany("INSERT INTO CYEAE_PRODUCT (NAME, PRICE, IS_ACTIVE, CATEGORY_ID) VALUES (?, ?, ?, ?)", products)
        
        customers = [
            ('John Smith', '13812345678', 'john@example.com', 'Kowloon', 'regular'),
            ('Sarah Johnson', '13987654321', 'sarah@example.com', 'Hong Kong Island', 'member'),
            ('Mike Wilson', '13555666777', 'mike@example.com', 'New Territories', 'regular')
        ]
        cursor.executemany("INSERT INTO CYEAE_CUSTOMER (NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE) VALUES (?, ?, ?, ?, ?)", customers)
        
        password_hash = hashlib.sha256('123456'.encode()).hexdigest()
        cursor.execute("""
            INSERT INTO CYEAE_MEMBER_CUSTOMERS (CUSTOMER_ID, PASSWORD_HASH, DATE_OF_BIRTH) 
            VALUES (2, ?, ?)
        """, (password_hash, '1990-05-15'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hash_value):
        return self.hash_password(password) == hash_value

class CoffeeShopDB:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_products(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.PRODUCT_ID, p.NAME, p.PRICE, p.IS_ACTIVE, c.CATEGORY_NAME
            FROM CYEAE_PRODUCT p
            LEFT JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
            WHERE p.IS_ACTIVE = 'Y'
            ORDER BY c.CATEGORY_NAME, p.NAME
        """)
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_categories(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CATEGORY_ID, CATEGORY_NAME, DESCRIPTION FROM CYEAE_CATEGORY ORDER BY CATEGORY_NAME")
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def create_customer(self, name, phone, email, address, customer_type='regular'):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CYEAE_CUSTOMER (NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, customer_type))
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id

    def create_member_customer(self, customer_id, password, date_of_birth=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self.db_manager.hash_password(password)
            cursor.execute(
                """
                INSERT INTO CYEAE_MEMBER_CUSTOMERS (CUSTOMER_ID, PASSWORD_HASH, DATE_OF_BIRTH)
                VALUES (?, ?, ?)
                """,
                (customer_id, password_hash, date_of_birth)
            )
            conn.commit()
        finally:
            conn.close()

    def get_member_by_email(self, email):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.CUSTOMER_ID, c.NAME, c.PHONE, c.EMAIL, c.ADDRESS, c.CUSTOMER_TYPE,
                   m.PASSWORD_HASH, m.DATE_OF_BIRTH, m.REGISTRATION_DATE
            FROM CYEAE_CUSTOMER c
            JOIN CYEAE_MEMBER_CUSTOMERS m ON c.CUSTOMER_ID = m.CUSTOMER_ID
            WHERE c.EMAIL = ?
            """,
            (email,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def verify_member_login(self, email, password):
        member = self.get_member_by_email(email)
        if not member:
            return None
        password_hash = member[6]
        if self.db_manager.verify_password(password, password_hash):
            return {
                'customer_id': member[0],
                'name': member[1],
                'phone': member[2],
                'email': member[3],
                'address': member[4],
                'customer_type': member[5],
                'date_of_birth': member[7],
                'registration_date': member[8]
            }
        return None
    
    def create_order(self, customer_id, payment_method, order_items):
        """创建订单"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 计算总金额
            total_amount = 0
            for item in order_items:
                cursor.execute("SELECT PRICE FROM CYEAE_PRODUCT WHERE PRODUCT_ID = ?", (item['product_id'],))
                price = cursor.fetchone()[0]
                total_amount += price * item['quantity']
            
            # 创建订单
            cursor.execute("""
                INSERT INTO CYEAE_ORDERS (CUSTOMER_ID, PAYMENT_METHOD, TOTAL_AMOUNT)
                VALUES (?, ?, ?)
            """, (customer_id, payment_method, total_amount))
            
            order_id = cursor.lastrowid
            
            # 添加订单项
            for item in order_items:
                cursor.execute("SELECT PRICE FROM CYEAE_PRODUCT WHERE PRODUCT_ID = ?", (item['product_id'],))
                unit_price = cursor.fetchone()[0]
                line_amount = unit_price * item['quantity']
                
                cursor.execute("""
                    INSERT INTO CYEAE_ORDER_ITEMS (ORDER_ID, PRODUCT_ID, QUANTITY, UNIT_PRICE, LINE_AMOUNT)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, item['product_id'], item['quantity'], unit_price, line_amount))
            
            conn.commit()
            return order_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_order_history(self, customer_id=None):
        """获取订单历史"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if customer_id:
            cursor.execute("""
                SELECT o.ORDER_ID, c.NAME, o.ORDER_DATE, o.STATUS, o.PAYMENT_METHOD, o.TOTAL_AMOUNT
                FROM CYEAE_ORDERS o
                JOIN CYEAE_CUSTOMER c ON o.CUSTOMER_ID = c.CUSTOMER_ID
                WHERE o.CUSTOMER_ID = ?
                ORDER BY o.ORDER_DATE DESC
            """, (customer_id,))
        else:
            cursor.execute("""
                SELECT o.ORDER_ID, c.NAME, o.ORDER_DATE, o.STATUS, o.PAYMENT_METHOD, o.TOTAL_AMOUNT
                FROM CYEAE_ORDERS o
                JOIN CYEAE_CUSTOMER c ON o.CUSTOMER_ID = c.CUSTOMER_ID
                ORDER BY o.ORDER_DATE DESC
            """)
        
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def get_order_details(self, order_id):
        """获取订单详情"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.PRODUCT_ID, p.NAME, oi.QUANTITY, oi.UNIT_PRICE, oi.LINE_AMOUNT
            FROM CYEAE_ORDER_ITEMS oi
            JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
            WHERE oi.ORDER_ID = ?
        """, (order_id,))
        
        items = cursor.fetchall()
        conn.close()
        return items
    
    def get_sales_report(self, start_date=None, end_date=None):
        """获取销售报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT 
                DATE(o.ORDER_DATE) as order_date,
                COUNT(o.ORDER_ID) as order_count,
                SUM(o.TOTAL_AMOUNT) as total_sales,
                AVG(o.TOTAL_AMOUNT) as avg_order_value
            FROM CYEAE_ORDERS o
            WHERE 1=1
        """
        
        params = []
        if start_date:
            base_query += " AND DATE(o.ORDER_DATE) >= ?"
            params.append(start_date)
        if end_date:
            base_query += " AND DATE(o.ORDER_DATE) <= ?"
            params.append(end_date)
            
        base_query += " GROUP BY DATE(o.ORDER_DATE) ORDER BY order_date DESC"
        
        cursor.execute(base_query, params)
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_product_sales_report(self):
        """获取产品销售报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
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
            ORDER BY total_revenue DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_customer_report(self):
        """获取客户报告"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
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
            ORDER BY total_spent DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report