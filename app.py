from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
import os
from flask_cors import CORS
from database import CoffeeShopDB
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'change-this-secret'  # for session
CORS(app)

db = CoffeeShopDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    data = request.form if request.form else request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return redirect(url_for('admin'))
    return render_template('admin_login.html', error='Invalid credentials'), 401

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = db.get_all_products()
        product_list = []
        for product in products:
            product_list.append({
                'id': product[0],
                'name': product[1],
                'price': float(product[2]),
                'is_active': product[3],
                'category': product[4]
            })
        return jsonify({'success': True, 'data': product_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.get_categories()
        category_list = []
        for category in categories:
            category_list.append({
                'id': category[0],
                'name': category[1],
                'description': category[2]
            })
        return jsonify({'success': True, 'data': category_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        customer_id = db.create_customer(
            name=data['name'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            customer_type=data.get('customer_type', 'regular')
        )
        return jsonify({'success': True, 'customer_id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Auth endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        address = data.get('address', '')
        date_of_birth = data.get('date_of_birth')

        if not all([name, email, password]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Create customer as member
        customer_id = db.create_customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            customer_type='member'
        )
        db.create_member_customer(customer_id, password, date_of_birth)

        return jsonify({'success': True, 'data': {
            'customer_id': customer_id,
            'name': name,
            'email': email
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not all([email, password]):
            return jsonify({'success': False, 'error': 'Missing email or password'}), 400

        member = db.verify_member_login(email, password)
        if not member:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        return jsonify({'success': True, 'data': member})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        customer_id = data.get('customer_id')
        if not customer_id:
            customer_id = db.create_customer(
                name=data['customer_name'],
                phone=data.get('customer_phone', ''),
                email=data.get('customer_email', ''),
                address=data.get('customer_address', '')
            )
        
        order_id = db.create_order(
            customer_id=customer_id,
            payment_method=data['payment_method'],
            order_items=data['items']
        )
        
        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        customer_id = request.args.get('customer_id')
        orders = db.get_order_history(customer_id)
        
        order_list = []
        for order in orders:
            order_list.append({
                'order_id': order[0],
                'customer_name': order[1],
                'order_date': order[2],
                'status': order[3],
                'payment_method': order[4],
                'total_amount': float(order[5])
            })
        
        return jsonify({'success': True, 'data': order_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/details', methods=['GET'])
def get_order_details(order_id):
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        items = db.get_order_details(order_id)
        
        item_list = []
        for item in items:
            item_list.append({
                'product_id': item[0],
                'product_name': item[1],
                'quantity': item[2],
                'unit_price': float(item[3]),
                'line_amount': float(item[4])
            })
        
        return jsonify({'success': True, 'data': item_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/sales', methods=['GET'])
def get_sales_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        report = db.get_sales_report(start_date, end_date)
        
        report_data = []
        for row in report:
            report_data.append({
                'date': row[0],
                'order_count': row[1],
                'total_sales': float(row[2]) if row[2] else 0,
                'avg_order_value': float(row[3]) if row[3] else 0
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/products', methods=['GET'])
def get_product_sales_report():
    try:
        report = db.get_product_sales_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'product_name': row[0],
                'category': row[1],
                'total_quantity': row[2],
                'total_revenue': float(row[3]) if row[3] else 0,
                'order_count': row[4]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/customers', methods=['GET'])
def get_customer_report():
    try:
        report = db.get_customer_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'customer_name': row[0],
                'customer_type': row[1],
                'order_count': row[2] if row[2] else 0,
                'total_spent': float(row[3]) if row[3] else 0,
                'avg_order_value': float(row[4]) if row[4] else 0,
                'last_order_date': row[5]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Serve images under /picture/* from static/picture directory
@app.route('/picture/<path:filename>')
def serve_picture(filename):
    pictures_dir = os.path.join(app.static_folder, 'picture')
    return send_from_directory(pictures_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)