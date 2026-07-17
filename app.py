from datetime import datetime 
from decimal import Decimal
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import razorpay

app = Flask(__name__)
app.config["SECRET_KEY"] = "easykirai-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///easykirai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    father_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    aadhaar_number = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False, default="Dehradun")
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship("Order", backref="student", lazy=True)
    
    def set_password(self, p):
        self.password_hash = generate_password_hash(p)
        
    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

class Retailer(db.Model):
    __tablename__ = "retailers"
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False)
    shop_name = db.Column(db.String(120), nullable=False)
    gstin = db.Column(db.String(20), nullable=False)
    business_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False, default="Dehradun")
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship("Product", backref="retailer", lazy=True)
    orders = db.relationship("Order", backref="retailer_obj", lazy=True)
    
    def set_password(self, p):
        self.password_hash = generate_password_hash(p)
        
    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    retailer_id = db.Column(db.Integer, db.ForeignKey("retailers.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Furniture, Electronics, Study
    description = db.Column(db.Text, nullable=False)
    price_per_month = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="AVAILABLE")
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship("Order", backref="product", lazy=True)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    retailer_id = db.Column(db.Integer, db.ForeignKey("retailers.id"), nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    # PENDING, ACTIVE, REJECTED, COMPLETED, CANCELLED
    retailer_note = db.Column(db.Text, nullable=True)
    expected_delivery = db.Column(db.String(120), nullable=True)
    razorpay_order_id = db.Column(db.String(100), nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default="UNPAID")
    # UNPAID, PAID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'student':
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

def retailer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'retailer':
            flash('Please log in as a retailer to access this page.', 'warning')
            return redirect(url_for('retailer_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    if session.get('user_role') == 'student':
        return redirect(url_for('home')) 
    elif session.get('user_role') == 'retailer':
        return redirect(url_for('retailer_dashboard'))
    return render_template('landing.html', hide_sidebar=True)

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        student = Student.query.filter_by(phone=phone).first()
        if student and student.check_password(password):
            session['user_id'] = student.id
            session['user_role'] = 'student'
            session['user_name'] = student.full_name
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid phone number or password.', 'danger')
    return render_template('student_login.html', hide_sidebar=True)

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        father_name = request.form.get('father_name')
        phone = request.form.get('phone')
        aadhaar_number = request.form.get('aadhaar_number')
        city = request.form.get('city', 'Dehradun')
        password = request.form.get('password')
        
        if Student.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('student_register'))
            
        new_student = Student(
            full_name=full_name,
            father_name=father_name,
            phone=phone,
            aadhaar_number=aadhaar_number,
            city=city
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('student_login'))
    return render_template('student_register.html', hide_sidebar=True)

@app.route('/retailer/login', methods=['GET', 'POST'])
def retailer_login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        retailer = Retailer.query.filter_by(phone=phone).first()
        if retailer and retailer.check_password(password):
            session['user_id'] = retailer.id
            session['user_role'] = 'retailer'
            session['user_name'] = retailer.contact_name
            flash('Login successful!', 'success')
            return redirect(url_for('retailer_dashboard'))
        flash('Invalid phone number or password.', 'danger')
    return render_template('retailer_login.html', hide_sidebar=True)

@app.route('/retailer/register', methods=['GET', 'POST'])
def retailer_register():
    if request.method == 'POST':
        contact_name = request.form.get('contact_name')
        phone = request.form.get('phone')
        shop_name = request.form.get('shop_name')
        gstin = request.form.get('gstin')
        business_address = request.form.get('business_address')
        city = request.form.get('city', 'Dehradun')
        password = request.form.get('password')
        
        if Retailer.query.filter_by(phone=phone).first():
            flash('Phone number already registered.', 'danger')
            return redirect(url_for('retailer_register'))
            
        new_retailer = Retailer(
            contact_name=contact_name,
            phone=phone,
            shop_name=shop_name,
            gstin=gstin,
            business_address=business_address,
            city=city
        )
        new_retailer.set_password(password)
        db.session.add(new_retailer)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('retailer_login'))
    return render_template('retailer_register.html', hide_sidebar=True)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('landing'))

@app.route('/retailer/logout')
def retailer_logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('retailer_login'))

@app.route('/home')
@student_login_required
def home():
    products = Product.query.filter_by(status='AVAILABLE').order_by(Product.created_at.desc()).limit(6).all()
    student_id = session.get('user_id')
    active_rentals = Order.query.filter_by(student_id=student_id, status='ACTIVE').count()
    # Calculate monthly spending (sum of price of active rentals)
    active_orders = Order.query.filter_by(student_id=student_id, status='ACTIVE').all()
    monthly_spending = sum([order.product.price_per_month for order in active_orders])
    
    dealers_nearby = Retailer.query.filter_by(city='Dehradun').count()
    total_saved = active_rentals * 150  # Dummy calculation for total saved
    
    return render_template('home.html', 
                           products=products, 
                           active_rentals=active_rentals, 
                           monthly_spending=monthly_spending,
                           dealers_nearby=dealers_nearby,
                           total_saved=total_saved)

@app.route('/products')
@student_login_required
def products():
    category = request.args.get('category')
    categories = ['Furniture', 'Electronics', 'Study']
    
    if category and category != 'All':
        products_list = Product.query.filter_by(category=category, status='AVAILABLE').all()
    else:
        products_list = Product.query.filter_by(status='AVAILABLE').all()
        category = 'All'
        
    return render_template('products.html', products=products_list, categories=categories, active_category=category)

@app.route('/product/<int:id>')
@student_login_required
def product_detail(id):
    product = Product.query.get_or_404(id)
    retailer = product.retailer
    student_id = session.get('user_id')
    existing_order = Order.query.filter_by(student_id=student_id, product_id=id).order_by(Order.created_at.desc()).first()
    
    return render_template('product_detail.html', product=product, retailer=retailer, existing_order=existing_order)

@app.route('/request/<int:id>', methods=['POST'])
@student_login_required
def request_product(id):
    product = Product.query.get_or_404(id)
    student_id = session.get('user_id')
    duration = int(request.form.get('duration_months', 1))
    
    # Check duplicate pending
    existing = Order.query.filter_by(student_id=student_id, product_id=id, status='PENDING').first()
    if existing:
        flash('You already have a pending request for this product.', 'warning')
        return redirect(url_for('product_detail', id=id))
        
    new_order = Order(
        student_id=student_id,
        product_id=id,
        retailer_id=product.retailer_id,
        duration_months=duration
    )
    db.session.add(new_order)
    db.session.commit()
    
    flash('Request sent to retailer successfully!', 'success')
    return redirect(url_for('product_detail', id=id))

@app.route('/my-rentals')
@student_login_required
def my_rentals():
    student_id = session.get('user_id')
    pending_orders = Order.query.filter_by(student_id=student_id, status='PENDING').all()
    active_orders = Order.query.filter_by(student_id=student_id, status='ACTIVE').all()
    completed_orders = Order.query.filter_by(student_id=student_id, status='COMPLETED').all()
    rejected_orders = Order.query.filter_by(student_id=student_id, status='REJECTED').all()
    
    return render_template('my_rentals.html', 
                           pending_orders=pending_orders,
                           active_orders=active_orders,
                           completed_orders=completed_orders,
                           rejected_orders=rejected_orders)

@app.route('/profile')
@student_login_required
def profile():
    student = Student.query.get(session.get('user_id'))
    active_now = Order.query.filter_by(student_id=student.id, status='ACTIVE').count()
    total_rentals = Order.query.filter_by(student_id=student.id).count()
    
    active_orders = Order.query.filter_by(student_id=student.id, status='ACTIVE').all()
    total_spent = sum([order.product.price_per_month * order.duration_months for order in active_orders])
    
    return render_template('profile.html', student=student, active_now=active_now, total_rentals=total_rentals, total_spent=total_spent)

@app.route('/wishlist')
@student_login_required
def wishlist():
    return render_template('wishlist.html')

@app.route('/messages')
@student_login_required
def messages():
    return render_template('messages.html')

@app.route('/settings')
@student_login_required
def settings():
    return render_template('settings.html')

@app.route('/retailer/dashboard')
@retailer_login_required
def retailer_dashboard():
    retailer_id = session.get('user_id')
    products = Product.query.filter_by(retailer_id=retailer_id).all()
    orders = Order.query.filter_by(retailer_id=retailer_id).all()
    
    total_products = len(products)
    total_orders = len(orders)
    pending_orders = [o for o in orders if o.status == 'PENDING']
    active_orders = [o for o in orders if o.status == 'ACTIVE']
    
    # Calculate earnings
    earnings = sum([o.product.price_per_month * o.duration_months for o in active_orders if o.payment_status == 'PAID'])
    
    return render_template('retailer_dashboard.html', 
                           products=products[:5], 
                           active_orders=len(active_orders),
                           pending_orders=pending_orders,
                           earnings=earnings,
                           total_products=total_products,
                           total_orders=total_orders)

@app.route('/retailer/products')
@retailer_login_required
def retailer_products():
    retailer_id = session.get('user_id')
    products = Product.query.filter_by(retailer_id=retailer_id).all()
    return render_template('retailer_products.html', products=products)

@app.route('/retailer/products/add', methods=['GET', 'POST'])
@retailer_login_required
def retailer_product_add():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        price_per_month = request.form.get('price_per_month')
        image_url = request.form.get('image_url')
        status = request.form.get('status', 'AVAILABLE')
        
        new_product = Product(
            retailer_id=session.get('user_id'),
            name=name,
            category=category,
            description=description,
            price_per_month=price_per_month,
            image_url=image_url,
            status=status
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('retailer_products'))
    return render_template('retailer_product_form.html', product=None)

@app.route('/retailer/products/<int:id>/edit', methods=['GET', 'POST'])
@retailer_login_required
def retailer_product_edit(id):
    product = Product.query.get_or_404(id)
    if product.retailer_id != session.get('user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('retailer_products'))
        
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.description = request.form.get('description')
        product.price_per_month = request.form.get('price_per_month')
        product.image_url = request.form.get('image_url')
        product.status = request.form.get('status')
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('retailer_products'))
        
    return render_template('retailer_product_form.html', product=product)

@app.route('/retailer/products/<int:id>/delete', methods=['POST'])
@retailer_login_required
def retailer_product_delete(id):
    product = Product.query.get_or_404(id)
    if product.retailer_id != session.get('user_id'):
        flash('Unauthorized.', 'danger')
        return redirect(url_for('retailer_products'))
        
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('retailer_products'))

@app.route('/retailer/orders')
@retailer_login_required
def retailer_orders():
    retailer_id = session.get('user_id')
    orders = Order.query.filter_by(retailer_id=retailer_id).order_by(Order.created_at.desc()).all()
    return render_template('retailer_orders.html', orders=orders)

@app.route('/retailer/orders/<int:id>/accept', methods=['POST'])
@retailer_login_required
def retailer_order_accept(id):
    order = Order.query.get_or_404(id)
    if order.retailer_id != session.get('user_id'):
        return redirect(url_for('retailer_orders'))
        
    order.status = 'ACTIVE'
    order.expected_delivery = request.form.get('expected_delivery')
    order.retailer_note = request.form.get('retailer_note')
    
    order.product.status = 'RENTED'
    
    db.session.commit()
    flash('Order accepted!', 'success')
    return redirect(url_for('retailer_orders'))

@app.route('/retailer/orders/<int:id>/reject', methods=['POST'])
@retailer_login_required
def retailer_order_reject(id):
    order = Order.query.get_or_404(id)
    if order.retailer_id != session.get('user_id'):
        return redirect(url_for('retailer_orders'))
        
    order.status = 'REJECTED'
    order.retailer_note = request.form.get('retailer_note')
    
    db.session.commit()
    flash('Order rejected.', 'danger')
    return redirect(url_for('retailer_orders'))

@app.route('/payment/create/<int:order_id>', methods=['POST'])
@student_login_required
def create_payment(order_id):
    order = Order.query.get_or_404(order_id)
    amount = int(order.product.price_per_month * order.duration_months * 100)
    payment_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"receipt_{order.id}"
    }
    try:
        razorpay_order = razorpay_client.order.create(data=payment_data)
        order.razorpay_order_id = razorpay_order['id']
        db.session.commit()
        return {"id": razorpay_order['id'], "amount": amount}
    except Exception as e:
        order.razorpay_order_id = f"mock_order_{order.id}"
        db.session.commit()
        return {"id": order.razorpay_order_id, "amount": amount}

@app.route('/payment/verify', methods=['POST'])
@student_login_required
def verify_payment():
    data = request.json
    try:
        order = Order.query.filter_by(razorpay_order_id=data.get('razorpay_order_id')).first()
        if order:
            order.payment_status = 'PAID'
            db.session.commit()
            flash('Payment successful!', 'success')
            return {"status": "success"}
    except:
        return {"status": "failed"}, 400
    return {"status": "failed"}, 400

if __name__ == "__main__":
    app.run(debug=True)
