from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_bootstrap5 import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
# csrf = CSRFProtect(app)  # Add CSRF protection
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Sample data function
def create_sample_data():
    """Create sample products if database is empty"""
    if Product.query.count() == 0:
        sample_products = [
            {
                'name': 'MacBook Pro M3',
                'description': 'Powerful laptop for professionals with M3 chip and stunning Retina display. Perfect for creative work and development.',
                'price': 1299.99,
                'image_url': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&h=300&fit=crop',
                'stock': 15,
                'category': 'Laptops'
            },
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest smartphone with titanium design, advanced camera system, and USB-C connectivity.',
                'price': 999.99,
                'image_url': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400&h=300&fit=crop',
                'stock': 25,
                'category': 'Phones'
            },
            {
                'name': 'AirPods Pro 2',
                'description': 'Wireless earbuds with active noise cancellation, spatial audio, and adaptive transparency.',
                'price': 249.99,
                'image_url': 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&h=300&fit=crop',
                'stock': 50,
                'category': 'Accessories'
            },
            {
                'name': 'iPad Air 5th Gen',
                'description': 'Versatile tablet with M1 chip, 10.9-inch Liquid Retina display, perfect for work and creativity.',
                'price': 599.99,
                'image_url': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop',
                'stock': 20,
                'category': 'Tablets'
            },
            {
                'name': 'Apple Watch Series 9',
                'description': 'Advanced smartwatch with health monitoring, fitness tracking, and always-on display.',
                'price': 399.99,
                'image_url': 'https://images.unsplash.com/photo-1510017803434-a899398421b3?w=400&h=300&fit=crop',
                'stock': 30,
                'category': 'Wearables'
            },
            {
                'name': 'Magic Keyboard',
                'description': 'Wireless keyboard with numeric keypad, scissor mechanism, and rechargeable battery.',
                'price': 149.99,
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=300&fit=crop',
                'stock': 40,
                'category': 'Accessories'
            },
            {
                'name': 'Studio Display',
                'description': '27-inch 5K Retina display with P3 wide color, True Tone, and anti-reflective coating.',
                'price': 1599.99,
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=300&fit=crop',
                'stock': 10,
                'category': 'Monitors'
            },
            {
                'name': 'Mac Mini M2',
                'description': 'Compact desktop computer with M2 chip, perfect for home office and creative projects.',
                'price': 599.99,
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=300&fit=crop',
                'stock': 18,
                'category': 'Computers'
            }
        ]

        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)

        db.session.commit()


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('Welcome back! You have successfully logged in.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered. Please use a different email.', 'danger')
            return render_template('register.html', form=form)

        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'danger')
            return render_template('register.html', form=form)

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Congratulations! Your account has been created successfully. You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'danger')

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent orders
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()

    # Get cart items count
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()

    # Get wishlist count
    wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()

    # Calculate total spent
    total_spent = db.session.query(db.func.sum(Order.total)).filter_by(user_id=current_user.id).scalar() or 0

    return render_template('dashboard.html',
                           recent_orders=recent_orders,
                           cart_count=cart_count,
                           wishlist_count=wishlist_count,
                           total_spent=total_spent)


@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search')

    query = Product.query

    if category:
        query = query.filter(Product.category == category)

    if search:
        query = query.filter(Product.name.contains(search) | Product.description.contains(search))

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = db.session.query(Product.category).distinct().all()

    return render_template('products.html',
                           products=products.items,
                           pagination=products,
                           categories=[cat[0] for cat in categories])


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()

    return render_template('product_detail.html',
                           product=product,
                           related_products=related_products)


@app.route('/cart')
@login_required
def cart():
    cart_items = db.session.query(CartItem).filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.product.price for item in cart_items)

    # Get recently viewed products (placeholder - you'd implement this with session tracking)
    recently_viewed = Product.query.limit(3).all()

    return render_template('cart.html',
                           cart_items=cart_items,
                           total=total,
                           recently_viewed=recently_viewed)


@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if product.stock <= 0:
        flash('Sorry, this product is out of stock.', 'warning')
        return redirect(url_for('products'))

    # Check if item already in cart
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if existing_item:
        existing_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{product.name} has been added to your cart!', 'success')
    return redirect(url_for('products'))


@app.route('/cart/update', methods=['POST'])
@login_required
# @csrf.exempt  # Exempt from CSRF for AJAX requests - use with caution
def update_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    action = data.get('action')

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=item_id
    ).first()

    if cart_item:
        if action == 'increase':
            if cart_item.product.stock > cart_item.quantity:
                cart_item.quantity += 1
            else:
                return jsonify({'success': False, 'message': 'Not enough stock available'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                db.session.delete(cart_item)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart updated successfully'})

    return jsonify({'success': False, 'message': 'Item not found'})


@app.route('/cart/remove', methods=['POST'])
@login_required
# @csrf.exempt  # Exempt from CSRF for AJAX requests - use with caution
def remove_from_cart():
    data = request.get_json()
    item_id = data.get('item_id')

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=item_id
    ).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart'})

    return jsonify({'success': False, 'message': 'Item not found'})


@app.route('/wishlist/add', methods=['POST'])
@login_required
# @csrf.exempt  # Exempt from CSRF for AJAX requests - use with caution
def add_to_wishlist():
    data = request.get_json()
    item_id = data.get('item_id')

    existing_item = WishlistItem.query.filter_by(
        user_id=current_user.id,
        product_id=item_id
    ).first()

    if existing_item:
        return jsonify({'success': False, 'message': 'Item already in wishlist'})

    wishlist_item = WishlistItem(user_id=current_user.id, product_id=item_id)
    db.session.add(wishlist_item)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Added to wishlist!'})


@app.route('/cart/promo', methods=['POST'])
@login_required
# @csrf.exempt  # Exempt from CSRF for AJAX requests - use with caution
def apply_promo():
    data = request.get_json()
    promo_code = data.get('promo_code', '').upper()

    # Sample promo codes
    promo_codes = {
        'SAVE10': 0.10,
        'WELCOME20': 0.20,
        'NEWUSER': 0.15
    }

    if promo_code in promo_codes:
        discount = promo_codes[promo_code]
        session['promo_discount'] = discount
        session['promo_code'] = promo_code
        return jsonify({
            'success': True,
            'message': f'Promo code applied! {int(discount * 100)}% discount'
        })

    return jsonify({'success': False, 'message': 'Invalid promo code'})


@app.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    subtotal = sum(item.quantity * item.product.price for item in cart_items)
    shipping = 0 if subtotal >= 50 else 9.99
    tax = subtotal * 0.08
    discount = session.get('promo_discount', 0) * subtotal
    total = subtotal + shipping + tax - discount

    return render_template('checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping=shipping,
                           tax=tax,
                           discount=discount,
                           total=total,
                           promo_code=session.get('promo_code'))


@app.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id) \
        .order_by(Order.created_at.desc()) \
        .paginate(page=page, per_page=10, error_out=False)

    return render_template('orders.html', orders=orders.items, pagination=orders)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(
            Product.name.contains(query) |
            Product.description.contains(query)
        ).all()
    else:
        products = []

    return render_template('search_results.html', products=products, query=query)


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Context processors
@app.context_processor
def inject_cart_count():
    cart_count = 0
    if current_user.is_authenticated:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return dict(cart_count=cart_count)


@app.context_processor
def inject_year():
    return dict(year=datetime.now().year)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run()
