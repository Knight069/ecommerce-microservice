# application/order_api/routes.py
from flask import jsonify, request, make_response
from . import order
from .. import db
from ..models import Order, OrderItem
from .api.UserClient import UserClient
from ..enums import OrderAddItemError, CheckoutError, FetchingOrderError
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@order.route('/api/orders', methods=['GET'])
def orders():
    """
    Retrieves all orders. This endpoint should likely only be accessed by admins.

    Returns:
        A JSON response containing a list of order details or an error message.

    Raises:
        Exception: If there's an error fetching orders from the database.
    """

    try:
        orders = [order.to_json() for order in Order.query.all()]
        response = jsonify(orders)
    except Exception as e:
        log.error(f"Error fetching orders: {e}")
        response = make_response(jsonify({'message': 'Internal server error'}), 500)
    return response


@order.route('/api/order/add-item', methods=['POST'])
def order_add_item():
    """
    Adds a product to the currently open order for the authorized user.

    Returns:
        A JSON response containing the updated order details or an error message.

    Raises:
        OrderAddItemError: If there's an error adding the item to the order.
    """

    try:
        # Check for authorization header
        api_key = request.headers.get('Authorization')
        if not api_key:
            log.debug("Missing Authorization header")
            return make_response(jsonify({'message': 'Not logged in'}), 401)

        # Verify user and retrieve user ID
        user_response = UserClient.get_user(api_key)
        if not user_response:
            log.debug("Invalid API key or user not found")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
        user = user_response['result']
        user_id = user['id']

        # Get product ID and quantity from request form
        product_id = int(request.form['product_id'])
        quantity = int(request.form['qty'])

        # Find or create an open order for the user
        open_order = Order.query.filter_by(user_id=user_id, is_open=1).first()
        if not open_order:
            log.info("No existing order, creating a new one")
            open_order = Order(user_id=user_id, is_open=True)

        # Check for existing item in the order and update quantity if found
        found = False
        for item in open_order.items:
            if item.product_id == product_id:
                found = True
                item.quantity += quantity
                break

        # Add new order item if not found in existing order
        if not found:
            log.info("Adding new item to order")
            open_order.items.append(OrderItem(product_id=product_id, quantity=quantity))

        # Save changes to the database
        db.session.add(open_order)
        db.session.commit()

        response = jsonify({'result': open_order.to_json()})
        log.info(response)
    except OrderAddItemError as e:
        log.error(e)
        raise e
    return response


@order.route('/api/order', methods=['GET'])
def order():
    """
    Retrieves the currently open order for the authorized user.

    Returns:
        A JSON response containing the order details or an error message.

    Raises:
        FetchingOrderError: If there's an error fetching the order.
    """

    try:
        # Check for authorization header
        api_key = request.headers.get('Authorization')
        if not api_key:
            log.debug("Missing Authorization header")
            return make_response(jsonify({'message': 'Not logged in'}), 401)

        # Verify user and retrieve user ID
        user_response = UserClient.get_user(api_key)
        if not user_response:
            log.debug("Invalid API key or user not found")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
        user = user_response['result']
        user_id = user['id']

        # Find the open order for the user
        open_order = Order.query.filter_by(user_id=user_id, is_open=1).first()

        if open_order is None:
            response = jsonify({'message': 'No open order found'})
        else:
            response = jsonify({'result': open_order.to_json()})
    except FetchingOrderError as e:
        log.error(e)
        raise e
    return response


@order.route('/api/order/checkout', methods=['POST'])
def checkout():
    """
    Marks the currently open order for the authorized user as closed (completed).

    Returns:
        A JSON response containing the details of the closed order or an error message.

    Raises:
        CheckoutError: If there's an error processing the checkout.
    """

    try:
        # Check for authorization header
        api_key = request.headers.get('Authorization')
        if not api_key:
            log.debug("Missing Authorization header")
            return make_response(jsonify({'message': 'Not logged in'}), 401)

        # Verify user and retrieve user ID
        user_response = UserClient.get_user(api_key)
        if not user_response:
            log.debug("Invalid API key or user not found")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
        user = user_response['result']
        user_id = user['id']

        # Find the open order for the user
        open_order = Order.query.filter_by(user_id=user_id, is_open=1).first()

        if not open_order:
            log.error("No open order found for checkout")
            return make_response(jsonify({'message': 'No open order to checkout'}), 400)

        # Close the order (set is_open to False)
        open_order.is_open = False

        # Save changes to the database
        db.session.add(open_order)
        db.session.commit()

        response = jsonify({'result': open_order.to_json()})
    except CheckoutError as e:
        log.error(e)
        raise e
    return response
