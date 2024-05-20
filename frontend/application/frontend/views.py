# application/frontend/views.py
import requests
from . import forms
from . import frontend
from .. import login_manager
from .api.UserClient import UserClient
from .api.ProductClient import ProductClient
from .api.OrderClient import OrderClient
from flask import render_template, session, redirect, url_for, flash, request

from flask_login import current_user


@login_manager.user_loader
def load_user(user_id):
    """Loads a user object from the user ID."""
    return None


@frontend.route('/', methods=['GET'])
def home():
    """Renders the home page with product listings.

    - Retrieves the current user from Flask-Login.
    - If the user is authenticated, retrieves the order from the session.
    - Handles potential `requests.exceptions.ConnectionError` during product retrieval.
    - Renders the home template with product data.
    """

    if current_user.is_authenticated:
        session['order'] = OrderClient.get_order_from_session()

    try:
        products = ProductClient.get_products()
    except requests.exceptions.ConnectionError:
        products = {
            'results': []
        }
        flash('Failed to retrieve products. Please try again later.', 'error')
        logger.error('Error fetching products from API: %s', requests.exceptions.ConnectionError)

    return render_template('home/index.html', products=products)


@frontend.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration.

    - Creates a registration form.
    - Validates form data on POST requests.
    - Checks for existing usernames before creating a new user.
    - Handles successful user creation and login redirection.
    - Flashes appropriate messages for errors or success.
    """

    form = forms.RegistrationForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            username = form.username.data

            # Search for existing user
            user = UserClient.does_exist(username)
            if user:
                # Existing user found
                flash('Username already exists. Please choose another.', 'error')
                return render_template('register/index.html', form=form)
            else:
                # Attempt to create new user
                user = UserClient.post_user_create(form)
                if user:
                    flash('Registration successful. Please login.', 'success')
                    return redirect(url_for('frontend.login'))

        else:
            flash('Registration form errors. Please check the fields.', 'error')

    return render_template('register/index.html', form=form)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login.

    - Redirects authenticated users to the home page.
    - Creates a login form.
    - Validates form data on POST requests.
    - Retrieves API key and user data on successful login.
    - Updates session with user and order data.
    - Flashes appropriate messages for errors or success.
    """

    if current_user.is_authenticated:
        return redirect(url_for('frontend.home'))
    form = forms.LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            api_key = UserClient.post_login(form)
            if api_key:
                session['user_api_key'] = api_key
                user = UserClient.get_user()
                session['user'] = user['result']

                order = OrderClient.get_order()
                if order.get('result', False):
                    session['order'] = order['result']

                flash('Welcome back, ' + user['result']['username'], 'success')
                return redirect(url_for('frontend.home'))
            else:
                flash('Invalid login credentials. Please try again.', 'error')
                logger.error('Login failed for user: %s', form.username.data)
        else:
            flash('Login form errors. Please check the fields.', 'error')
    return render_template('login/index.html', form=form)


@frontend.route('/logout', methods=['GET'])
def logout():
    """Logs out the user and clears the session.

    - Clears the session data.
    - Redirects to the home page.
    """

    session.clear()  # type: ignore
    return redirect(url_for('frontend.home'))


@frontend.route('/product/<slug>', methods=['GET', 'POST'])
def product(slug):
    """Renders the product details page and handles adding items to cart.

    - Retrieves a product by its slug.
    - Creates an item form associated with the product ID.
    - Handles form submission for adding items to the cart.
    - Checks for logged-in users before adding items.
    - Flashes appropriate messages for errors or success.
    - Updates session data with the updated order.
    """

    response = ProductClient.get_product(slug)
    item = response['result']

    form = forms.ItemForm(product_id=item['id'])

    if request.method == "POST":
        if 'user' not in session:
            flash('Please login to add items to your cart.', 'error')
            return redirect(url_for('frontend.login'))
        order = OrderClient.post_add_to_cart(product_id=item['id'], qty=1)
        new_func(order)
        flash('Item added to your cart.', 'success')
    return render_template('product/index.html', product=item, form=form)


def new_func(order):
    """Updates the session with the new order data.

    - Updates the session's 'order' key with the new order data.
    """

    session['order'] = order['result']


@frontend.route('/checkout', methods=['GET'])
def summary():
    """Renders the checkout summary page.

    - Checks for logged-in users and a valid order in the session.
    - Redirects to login or home page in case of missing data.
    - Retrieves the order details from the OrderClient.
    - Checks for an empty order before rendering the checkout page.
    - Redirects to home page if the order is empty.
    - Processes checkout (handled by OrderClient).
    - Redirects to the thank you page on successful checkout.
    """

    if 'user' not in session:
        flash('Please login to proceed with checkout.', 'error')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash('No order found in your cart.', 'error')
        return redirect(url_for('frontend.home'))
    order = OrderClient.get_order()

    if len(order['result']['items']) == 0:
        flash('No items found in your cart.', 'error')
        return redirect(url_for('frontend.home'))

    OrderClient.post_checkout()

    return redirect(url_for('frontend.thank_you'))


@frontend.route('/order/thank-you', methods=['GET'])
def thank_you():
    """Renders the thank you page after successful checkout.

    - Checks for logged-in users and a valid order in the session.
    - Redirects to login or home page in case of missing data.
    - Removes the order data from the session.
    - Flashes a success message for the completed order.
    """

    if 'user' not in session:
        flash('Please login to view your order details.', 'error')
        return redirect(url_for('frontend.login'))

    if 'order' not in session:
        flash('No order found. Your order may have already been processed.', 'error')
        return redirect(url_for('frontend.home'))

    session.pop('order', None)  # type: ignore
    flash('Thank you for your order! Your confirmation details have been sent to your email.', 'success')

    return render_template('order/thankyou.html')


@frontend.context_processor
def base():
    """Provides a search form to all templates.

    - Creates a search form instance.
    - Returns the form as a context variable.
    """

    form = forms.SearchForm()
    return dict(form=form)


@frontend.route('/search', methods=['GET', 'POST'])
def search():
    """Handles product search based on form submission.

    - Creates a search form.
    - Validates form data on POST requests.
    - Handles potential `requests.exceptions.ConnectionError` during product retrieval.
    - Renders the home template with filtered products (if search is successful).
    """

    form = forms.SearchForm()
    if form.validate_on_submit():
        search_term = form.search.data
        try:
            products = ProductClient.search_products(search_term)
        except requests.exceptions.ConnectionError:
            products = {
                'results': []
            }
            flash('Failed to search for products. Please try again later.', 'error')
            logger.error('Error searching products: %s', requests.exceptions.ConnectionError)
        else:
            flash('Search results for: ' + search_term, 'info')
            return render_template('home/index.html', products=products.get('results', []))  # Use .get to handle potential missing 'results' key

    return render_template('search/index.html', form=form)
