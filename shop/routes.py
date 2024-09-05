from flask import Flask, render_template, session, request, redirect, url_for, flash, current_app, make_response, \
    send_file
from flask_login import login_required, current_user, login_user, logout_user
from shop import app, db, bcrypt, photos, search, login_manager
from flask_cors import CORS
from io import BytesIO
from xhtml2pdf import pisa
from .forms import RegistrationForm, LoginForms, Addprouducts

from .models import User, Addproduct, Brand, Category, Report, Contact
from .cus_forms import CustomerRegisterForm, CustomerLoginForm
from .cus_model import Register, JsonEcodedDict, CustomerOrder
import secrets, os
import pdfkit
import stripe
import json
import pdfcrowd

publishable_key = 'pk_test_51OzYGIFbXs92LSWUxVJ1AApNnbLYTZ0fkXuCl9iIxjeWBGnFNHlk8zqjvkyBPjuginusR7fJhZ6d7LytKbpPRFgI00gUprrcKU'

stripe.api_key = 'sk_test_51OzYGIFbXs92LSWUHdBUS9m3cE2RcSN6AZLw8wVe4TT0RardrLeg5JhzacQ9aI6xtMRFwOJKnpH14Ve29RcQHkEB00Vp47vzDS'


#
# @app.route('/thanks')
# def thanks():
#     invoice_number = request.args.get('invoice')
#     delivery_info = "Your delivery will be delivered within 2 days."
#     return render_template('customer/thanks.html', invoice_number=invoice_number, delivery_info=delivery_info)

@app.route('/thanks/<invoice_number>')  # Ensure it correctly accepts invoice_number
def thanks(invoice_number):
    delivery_info = "Your delivery will be delivered within 2 days."
    return render_template('customer/thanks.html', invoice_number=invoice_number, delivery_info=delivery_info)


def brands1():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands


def categories1():
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return categories


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page,
                                                                                                     per_page=8)
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return render_template('products/display.html', products=products, brands=brands, categories=categories)


@app.route('/result')
def result():
    keyword = request.args.get('q')
    products = Addproduct.query.msearch(keyword, fields=['name', 'description'], limit=3)
    return render_template('products/result.html', products=products, brands=brands1(), categories=categories1())


@app.route('/products/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return render_template('products/single_page.html', product=product, brands=brands, categories=categories)


@app.route('/brand/<int:id>')
def get_brand(id):
    get_d = Brand \
        .query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    brand = Addproduct.query.filter_by(brand=get_d).paginate(page=page, per_page=8)
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id))
    return render_template('products/display.html', brand=brand, brands=brands, categories=categories, get_d=get_d)


@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=8)
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    categories = Category.query.join(Addproduct, (Category.id == Addproduct.category_id)).all()
    return render_template('products/display.html', get_cat_prod=get_cat_prod, categories=categories, brands=brands,
                           get_cat=get_cat)


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    products = Addproduct.query.all()
    return render_template('admin/index.html', title='Admin page', products=products)


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title='brands', brands=brands)


@app.route('/categories')
def categories():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title='categories', categories=categories)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()  # Commit changes to the database
        flash(f'Welcome {form.name.data} thank you for registering', 'success')

        return redirect(url_for('login'))  # Redirect after successful registration
    return render_template('admin/register.html', form=form, title="Registration page")


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForms(request.form)
#     if request.method == "POST" and form.validate():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             session['email'] = form.email.data
#             flash(f'Welcome {form.email.data} You are logged in now', 'success')
#             return redirect(request.args.get('next') or url_for('admin'))
#         else:
#             flash('Wrong Password. Please try again', 'danger')
#     # else:
#     #     flash('Form validation failed.Please try again', 'danger')
#
#     return render_template('admin/login.html', form=form, title="login page")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForms(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data

            return redirect(request.args.get('next') or url_for('admin'))
        else:

            # Optionally, log failed login attempts for debugging
            app.logger.warning(f'Failed login attempt for email: {form.email.data}')
            # You might want to redirect back to the login page instead
            # return redirect(url_for('login'))
    return render_template('admin/login.html', form=form, title="Login Page")


@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('brands'))

    return render_template('products/addbrand.html', brands="brands")


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Login first please', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'The brand {updatebrand.name} was changed to {brand}', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    # brand = updatebrand.name
    return render_template('products/updatebrand.html', title='Update brand page', brands='brands',
                           updatebrand=updatebrand)


@app.route('/deletebrand/<int:id>', methods=['GET', 'POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        flash(f"The brand {brand.name} was deleted from your database", "success")
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f"The brand {brand.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin'))


@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getcat = request.form.get('category')
        cat = Category(name=getcat)
        db.session.add(cat)
        flash(f'The Category  {getcat} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('categories'))

    return render_template('products/addbrand.html')


#
@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    if 'email' not in session:
        flash('Login first please', 'danger')
        return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecat.name = category
        flash(f'The category {updatecat.name} was changed to {category}', 'success')

        db.session.commit()
        return redirect(url_for('categories'))
    category = updatecat.name
    return render_template('products/updatebrand.html', title='Update cat', updatecat=updatecat)


@app.route('/deletecategory/<int:id>', methods=['GET', 'POST'])
def deletecat(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        flash(f"The category {category.name} was deleted from your database", "success")
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f"The brand {category.name} can't be  deleted from your database", "warning")
    return redirect(url_for('admin'))


@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addprouducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')

        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

        addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                            description=description,
                            category_id=category, brand_id=brand, image_1=image_1,
                            image_2=image_2, image_3=image_3)
        db.session.add(addpro)

        flash(f'The product {name} has been add to the data base', 'success')
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('products/addproduct.html', title="Add products", form=form, brands=brands,
                           categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    form = Addprouducts(request.form)
    product = Addproduct.query.get_or_404(id)
    brands = Brand.query.all()
    categories = Category.query.all()
    brand = request.form.get('brand')
    category = request.form.get('category')
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.colors = form.colors.data
        product.description = form.description.data
        product.category_id = category
        product.brand_id = brand
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash('The product was updated', 'success')

        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description
    brand = product.brand.name
    category = product.category.name
    return render_template('products/updateproduct.html', form=form, title='Update Product', brands=brands,
                           categories=categories, product=product)


# @app.route('/deleteproduct/<int:id>', methods=['POST'])
# def deleteproduct(id):
#     product = Addproduct.query.get_or_404(id)
#     if request.method == "POST":
#         try:
#             os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
#             os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
#             os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
#         except Exception as e:
#             print(e)
#         db.session.delete(product)
#         db.session.commit()
#         flash(f'The product {product.name} was delete from your record', 'success')
#         return redirect(url_for('admin'))
#     flash(f'Can not delete the product', 'success')
#     return redirect(url_for('admin'))


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            flash(f'An error occurred while deleting the product: {str(e)}', 'danger')
            return redirect(url_for('admin'))

        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} was deleted from your record', 'success')
        return redirect(url_for('admin'))
    flash(f'Cannot delete the product', 'danger')
    return redirect(url_for('admin'))


@app.route('/report')
def price_range_report():
    # Query products from the database
    products = Addproduct.query.all()

    # Count the number of products falling into each price range
    below_100 = sum(product.price < 100 for product in products)
    between_100_and_1000 = sum(100 <= product.price < 1000 for product in products)
    above_1000 = sum(product.price >= 1000 for product in products)

    # Calculate percentages
    total_products = len(products)
    percentage_below_100 = (below_100 / total_products) * 100
    percentage_between_100_and_1000 = (between_100_and_1000 / total_products) * 100
    percentage_above_1000 = (above_1000 / total_products) * 100

    # Render the template with data for the pie chart
    return render_template('price_range_report.html',
                           percentages=[percentage_below_100, percentage_between_100_and_1000, percentage_above_1000])


@app.route('/addcart', methods=['POST'])
def Addcart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method == "POST":
            DictItems = {product_id: {'name': product.name, 'price': product.price, 'discount': product.discount,
                                      'color': colors, 'quantity': quantity, 'image': product.image_1,
                                      'colors': product.colors}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session:
                    for key, item in session['shoppingcart'].items():
                        if int(key) == int(product.id):
                            session.modify = True
                            item['quantity'] += 1

                else:
                    session['Shoppingcart'] = MergeDicts(session['Shoppingcart'], DictItems)

                    return redirect(request.referrer)

            else:
                session['Shoppingcart'] = DictItems
                return redirect(request.referrer)


    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


def MergeDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route('/carts')
def getCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        # return redirect(url_for('home'))
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount'] / 100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (0.06 * float(subtotal)))
        grandtotal = float("%.2f" % (1.06 * subtotal))
    return render_template('products/carts.html', tax=tax, grandtotal=grandtotal, brands=brands(),
                           categories=categories())


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('home'))
    except Exception as e:
        print(e)


@app.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash('Item is updated!')
                    return redirect(url_for('getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('getCart'))


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getCart'))


@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)


# coustomer part
@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data,
                            username=form.username.data,
                            email=form.email.data,
                            password=hash_password,
                            country=form.country.data,
                            state=form.state.data,
                            contact=form.contact.data,
                            city=form.city.data,
                            address=form.address.data,
                            zipcode=form.zipcode.data)
        db.session.add(register)

        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))

    return render_template('products/cus_register.html', form=form)


@app.route('/customer/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are logged in now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email or password ', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customer/login.html', form=form)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('customerLogin'))


def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            # return redirect(url_for('orders', invoice=invoice))
            return redirect(url_for('orders', invoice=invoice))

        except Exception as e:
            print(e)
            flash(f'Something went wrong', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
            CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal,
                           customer=customer, orders=orders)


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method == "POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
                CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount'] / 100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = ("%.2f" % (1.06 * float(subTotal)))

            rendered = render_template('customer/pdf.html', invoice=invoice, tax=tax, grandTotal=grandTotal,
                                       customer=customer, orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline: filename=' + invoice + '.pdf'
            return response
        return request(url_for('orders'))


# @app.route('/generate_pdf', methods=['POST'])
# def generate_pdf():
#     html_content = request.json.get('htmlContent', '')
#
#     pdf = pdfkit.from_string(html_content, False)
#
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'attachment; filename=invoice.pdf'
#
#     return response


@app.route('/payment', methods=['POST'])
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        description='Myshop',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).order_by(
        CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks', invoice_number=invoice))


# @app.route('/generate_pdf', methods=['GET', 'POST'])
# def generate_pdf():
#     print("Request received")
#     try:
#         # Get HTML content from the request
#         html_content = request.json.get('htmlContent')
#
#         # Create a BytesIO object to store the PDF
#         pdf = BytesIO()
#
#         # Generate PDF from HTML content
#         pisa.CreatePDF(html_content, dest=pdf)
#
#         # Set the position of the BytesIO object to the beginning
#         pdf.seek(0)
#
#         # Return the PDF as a file attachment
#         return send_file(
#             pdf,
#             as_attachment=True,
#             attachment_filename='invoice.pdf',
#             mimetype='application/pdf'
#         )
#     except Exception as e:
#         return str(e), 500


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        new_message = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('admin/contact.html')
