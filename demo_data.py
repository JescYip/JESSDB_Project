#!/usr/bin/env python3
"""
Demo Data Generator - Fixed Version
Generate additional demo data for Coffee Ordering System
All data in English to match the system requirements
"""

from database import CoffeeShopDB
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Generate demo data with English names and proper formatting"""
    db = CoffeeShopDB()
    
    print("🎭 Generating demo data...")
    
    # Create more customers with English names
    customers = [
        ('Alice Johnson', '13912345678', 'alice@example.com', 'Kowloon', 'regular'),
        ('Bob Smith', '13823456789', 'bob@example.com', 'Hong Kong Island', 'member'),
        ('Carol Davis', '13734567890', 'carol@example.com', 'New Territories', 'regular'),
        ('David Wilson', '13645678901', 'david@example.com', 'Kowloon', 'member'),
        ('Emma Brown', '13556789012', 'emma@example.com', 'Hong Kong Island', 'regular'),
        ('Frank Miller', '13467890123', 'frank@example.com', 'New Territories', 'regular'),
        ('Grace Lee', '13378901234', 'grace@example.com', 'Kowloon', 'member'),
        ('Henry Taylor', '13289012345', 'henry@example.com', 'Hong Kong Island', 'regular'),
    ]
    
    customer_ids = []
    for customer in customers:
        try:
            customer_id = db.create_customer(*customer)
            customer_ids.append(customer_id)
            print(f"✅ Created customer: {customer[0]}")
        except Exception as e:
            print(f"⚠️  Customer {customer[0]} may already exist")
    
    # Get all products
    products = db.get_all_products()
    product_ids = [p[0] for p in products]
    
    # Generate historical orders (past 30 days)
    print("\n📦 Generating historical orders...")
    payment_methods = ['cash', 'card', 'alipay', 'wechat']
    
    for i in range(50):  # Generate 50 orders
        # Random date (within past 30 days)
        days_ago = random.randint(0, 30)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        # Random customer selection
        customer_id = random.choice(customer_ids + [1, 2, 3])  # Include existing customers
        
        # Random order items
        num_items = random.randint(1, 5)
        order_items = []
        
        for _ in range(num_items):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 3)
            
            # Avoid duplicate products
            if not any(item['product_id'] == product_id for item in order_items):
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity
                })
        
        if order_items:  # Ensure we have order items
            try:
                payment_method = random.choice(payment_methods)
                order_id = db.create_order(customer_id, payment_method, order_items)
                
                # Update order date (simulate historical orders)
                conn = db.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE CYEAE_ORDERS SET ORDER_DATE = ? WHERE ORDER_ID = ?",
                    (order_date.strftime('%Y-%m-%d %H:%M:%S'), order_id)
                )
                conn.commit()
                conn.close()
                
                print(f"✅ Created order #{order_id} ({order_date.strftime('%Y-%m-%d')})")
                
            except Exception as e:
                print(f"❌ Failed to create order: {e}")
    
    print("\n🎉 Demo data generation completed!")
    print("\n📊 Data Statistics:")
    
    # Display statistics
    sales_report = db.get_sales_report()
    total_sales = sum(row[2] if row[2] else 0 for row in sales_report)
    total_orders = sum(row[1] for row in sales_report)
    
    print(f"📈 Total Sales: ${total_sales:.2f}")
    print(f"📦 Total Orders: {total_orders}")
    print(f"💰 Average Order Value: ${total_sales/total_orders if total_orders > 0 else 0:.2f}")
    
    product_report = db.get_product_sales_report()
    print(f"🏆 Most Popular Product: {product_report[0][0] if product_report else 'None'}")
    
    customer_report = db.get_customer_report()
    active_customers = len([c for c in customer_report if c[2] > 0])
    print(f"👥 Active Customers: {active_customers}")

if __name__ == '__main__':
    generate_demo_data()