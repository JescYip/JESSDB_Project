// 全局变量
let products = [];
let cart = [];
let currentTab = 'menu';
let currentUser = null; 

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
async function initializeApp() {
    try {
        await loadProducts();
        setupEventListeners();
        showTab('menu');
        wireAccountForms();
    } catch (error) {
        console.error('Initialization failed:', error);
        showAlert('System initialization failed. Please refresh the page and try again.', 'error');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 导航标签点击事件
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            showTab(tabName);
        });
    });

    // 订单表单提交
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', handleOrderSubmit);
    }
}

// 绑定登录/注册表单事件
function wireAccountForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const payload = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            try {
                const resp = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await resp.json();
                if (result.success) {
                    currentUser = result.data;
                    showAlert('Signed in successfully', 'success');
                } else {
                    throw new Error(result.error || 'Login failed');
                }
            } catch (err) {
                console.error(err);
                showAlert('Login failed', 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const payload = {
                name: formData.get('name'),
                email: formData.get('email'),
                password: formData.get('password'),
                phone: formData.get('phone'),
                address: formData.get('address'),
                date_of_birth: formData.get('date_of_birth')
            };
            try {
                const resp = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await resp.json();
                if (result.success) {
                    showAlert('Account created. You can sign in now.', 'success');
                    loginForm && loginForm.reset();
                    registerForm.reset();
                } else {
                    throw new Error(result.error || 'Registration failed');
                }
            } catch (err) {
                console.error(err);
                showAlert('Registration failed', 'error');
            }
        });
    }
}

// 加载产品数据
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const result = await response.json();
        
        if (result.success) {
            products = result.data;
            renderProducts();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load product:', error);
        showAlert('Failed to load product', 'error');
    }
}

// 渲染产品列表
function renderProducts() {
    const container = document.getElementById('productsContainer');
    if (!container) return;

    container.innerHTML = '';
    
    // 按分类分组产品
    const categories = {};
    products.forEach(product => {
        if (!categories[product.category]) {
            categories[product.category] = [];
        }
        categories[product.category].push(product);
    });

    // 渲染每个分类的产品
    Object.keys(categories).forEach(categoryName => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'category-section';
        categoryDiv.innerHTML = `
            <h2 style="color: #4a5568; margin: 20px 0 15px 0; font-size: 1.5em;">${categoryName}</h2>
            <div class="products-grid" id="category-${categoryName}"></div>
        `;
        container.appendChild(categoryDiv);

        const categoryGrid = document.getElementById(`category-${categoryName}`);
        categories[categoryName].forEach(product => {
            const productCard = createProductCard(product);
            categoryGrid.appendChild(productCard);
        });
    });
}

// 创建产品卡片
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    // 手动指定每个产品的图片路径
    const imageMap = {
        'Americano': '/picture/americano.jpg',
        'Latte': '/picture/latte.jpg',
        'Cappuccino': '/picture/Cappuccino.jpg',
        'Mocha': '/picture/Mocha.jpg',
        'chinesetea': '/picture/chinesetea.jpg',
        'Milk Tea': '/picture/Milktea.jpg',
        'Cheesecake': '/picture/cheesecake.jpg',
        'Tiramisu': '/picture/tiramisu.jpg',
        'Ham Sandwich': '/picture/HamSandwich.jpg',
        'Caesar Salad': '/picture/caesarsalad.jpg'
    };
    
    const imgSrc = imageMap[product.name] || '/picture/default.jpg';
    
    card.innerHTML = `
        <img class="product-image" src="${imgSrc}" alt="${product.name}" />
        <h3>${product.name}</h3>
        <div class="category">${product.category}</div>
        <div class="price">$${product.price.toFixed(2)}</div>
        <div class="quantity-control">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, -1)">-</button>
            <input type="number" class="quantity-input" id="qty-${product.id}" value="1" min="1" max="99">
            <button class="quantity-btn" onclick="changeQuantity(${product.id}, 1)">+</button>
        </div>
        <button class="add-to-cart" onclick="addToCart(${product.id})">
            Add to Cart
        </button>
    `;
    return card;
}

// 将产品名转为图片文件名（小写、去空格和特殊字符）
/*function slugifyProductName(name) {
    return String(name)
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '');
}*/

// 修改数量
function changeQuantity(productId, change) {
    const input = document.getElementById(`qty-${productId}`);
    const currentValue = parseInt(input.value);
    const newValue = Math.max(1, Math.min(99, currentValue + change));
    input.value = newValue;
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value);
    
    if (!product) return;

    const existingItem = cart.find(item => item.product_id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            product_id: productId,
            name: product.name,
            price: product.price,
            quantity: quantity
        });
    }

    updateCartDisplay();
    showAlert(`${product.name} added to cart`, 'success');
    
    document.getElementById(`qty-${productId}`).value = 1;
}

// 更新购物车显示
function updateCartDisplay() {
    const cartContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    
    if (!cartContainer || !cartTotal) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = '<p style="text-align: center; color: #718096;">Your cart is empty</p>';
        cartTotal.textContent = 'Total: $0.00';
        return;
    }

    let total = 0;
    cartContainer.innerHTML = '';

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <div>
                <strong>${item.name}</strong><br>
                <small>$${item.price.toFixed(2)} x ${item.quantity}</small>
            </div>
            <div>
                <span style="margin-right: 10px;">$${itemTotal.toFixed(2)}</span>
                <button class="btn-danger" style="padding: 5px 10px; font-size: 0.8em;" onclick="removeFromCart(${index})">Remove</button>
            </div>
        `;
        cartContainer.appendChild(cartItem);
    });

    cartTotal.textContent = `Total: $${total.toFixed(2)}`;
}

// 从购物车移除商品
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
    showAlert('Item removed from cart', 'info');
}

// 清空购物车
function clearCart() {
    cart = [];
    updateCartDisplay();
    showAlert('Cart cleared', 'info');
}

// 处理订单提交
async function handleOrderSubmit(e) {
    e.preventDefault();
    
    if (cart.length === 0) {
        showAlert('Your cart is empty. Please add items first.', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const orderData = {
        customer_name: formData.get('customer_name'),
        customer_phone: formData.get('customer_phone'),
        customer_email: formData.get('customer_email'),
        customer_address: formData.get('customer_address'),
        payment_method: formData.get('payment_method'),
        items: cart
    };

    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();
        
        if (result.success) {
            showAlert(`Order created! ID: ${result.order_id}`, 'success');
            clearCart();
            document.getElementById('orderForm').reset();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Create order failed:', error);
        showAlert('Failed to create order. Please try again.', 'error');
    }
}

// 显示标签页
function showTab(tabName) {
    // 更新导航标签
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // 更新内容区域
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    currentTab = tabName;

    // Orders tab removed for public site; admin handles orders
}

// 加载订单历史
async function loadOrderHistory() {
    try {
        const response = await fetch('/api/orders');
        const result = await response.json();
        
        if (result.success) {
            renderOrderHistory(result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Load order history failed:', error);
        showAlert('Failed to load order history', 'error');
    }
}

// 渲染订单历史
function renderOrderHistory(orders) {
    const container = document.getElementById('ordersContainer');
    if (!container) return;

    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #718096;">No orders yet</p>';
        return;
    }

    const table = document.createElement('table');
    table.className = 'table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Order Date</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Total</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            ${orders.map(order => `
                <tr>
                    <td>#${order.order_id}</td>
                    <td>${order.customer_name}</td>
                            <td>${new Date(order.order_date).toLocaleString('en-US')}</td>
                    <td><span class="status-${order.status}">${getStatusText(order.status)}</span></td>
                    <td>${getPaymentMethodText(order.payment_method)}</td>
                    <td>$${order.total_amount.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 0.8em;" onclick="viewOrderDetails(${order.order_id})">Details</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    container.innerHTML = '';
    container.appendChild(table);
}

// 查看订单详情
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/orders/${orderId}/details`);
        const result = await response.json();
        
        if (result.success) {
            showOrderDetailsModal(orderId, result.data);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load order details:', error);
        showAlert('Failed to load order details', 'error');
    }
}

function showOrderDetailsModal(orderId, items) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 15px;
        max-width: 600px;
        width: 90%;
        max-height: 80%;
        overflow-y: auto;
    `;

    let total = 0;
    items.forEach(item => {
        total += item.line_amount;
    });

    content.innerHTML = `
        <h2 style="margin-bottom: 20px; color: #4a5568;">Order Details #${orderId}</h2>
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Qty</th>
                    <th>Unit Price</th>
                    <th>Subtotal</th>
                </tr>
            </thead>
            <tbody>
                ${items.map(item => `
                    <tr>
                        <td>${item.product_name}</td>
                        <td>${item.quantity}</td>
                        <td>$${item.unit_price.toFixed(2)}</td>
                        <td>$${item.line_amount.toFixed(2)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
        <div style="text-align: right; margin-top: 20px; font-size: 1.2em; font-weight: bold; color: #4a5568;">
            Total: $${total.toFixed(2)}
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">Close</button>
        </div>
    `;

    modal.className = 'modal';
    modal.appendChild(content);
    document.body.appendChild(modal);

    // 点击背景关闭模态框
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'pending': 'Pending',
        'processing': 'Processing',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
}

// 获取支付方式文本
function getPaymentMethodText(method) {
    const methodMap = {
        'cash': 'Cash',
        'card': 'Card',
        'alipay': 'Alipay',
        'wechat': 'WeChat Pay'
    };
    return methodMap[method] || method;
}

// 显示提示消息
function showAlert(message, type = 'info') {
    // 移除现有的提示
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    // 插入到内容区域顶部
    const content = document.querySelector('.content');
    content.insertBefore(alert, content.firstChild);

    // 3秒后自动移除
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
}