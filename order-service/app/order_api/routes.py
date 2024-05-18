# application/order_api/routes.py
from flask import jsonify, request, make_response
from git import CheckoutError

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
    This API fetches orders of the user
    :return:
    """
    try:
        items = []
        for row in Order.query.all():
            items.append(row.to_json())
        log.info(f"Items for order: {items}")
        response = jsonify(items)
    except Exception as e:
        log.error(e)
        raise e
    return response


@order.route('/api/order/add-item', methods=['POST'])
def order_add_item():
    """
    This API add items to the cart for the User
    :return:
    """
    try:
        api_key = request.headers.get('Authorization')
        log.info("checking for Authorization")
        response = UserClient.get_user(api_key)
        if not response:
            log.debug("Not logged in")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
        log.info("Authorized")
        user = response['result']
        p_id = int(request.form['product_id'])
        qty = int(request.form['qty'])
        u_id = int(user['id'])
        # Filtering order by user_id
        known_order = Order.query.filter_by(user_id=u_id, is_open=1).first()
        # If no order exists for the user
        if known_order is None:
            log.info("No existing orders for user creating new order")
            known_order = Order()
            known_order.is_open = True
            known_order.user_id = u_id
            # ordering Item for the user
            order_item = OrderItem(p_id, qty)
            known_order.items.append(order_item)
        # if an order already exists increase quantity
        else:
            log.info("New Item adding")
            found = False
            #
            for item in known_order.items:
                if item.product_id == p_id:
                    found = True
                    item.quantity += qty
            log.info("Item Added")
            if found is False:
                order_item = OrderItem(p_id, qty)
                known_order.items.append(order_item)

        db.session.add(known_order)
        db.session.commit()
        response = jsonify({'result': known_order.to_json()})
        log.info(response)
    except OrderAddItemError as e:
        log.error(e)
        raise e
    return response


@order.route('/api/order', methods=['GET'])
def order():
    """
    This API gets order of the user
    :return:
    """
    try:
        api_key = request.headers.get('Authorization')

        response = UserClient.get_user(api_key)

        if not response:
            return make_response(jsonify({'message': 'Not logged in'}), 401)

        user = response['result']
        open_order = Order.query.filter_by(user_id=user['id'], is_open=1).first()

        if open_order is None:
            response = jsonify({'message': 'No order found'})
        else:
            response = jsonify({'result': open_order.to_json()})
    except FetchingOrderError as e:
        log.error(e)
        raise e
    return response


@order.route('/api/order/checkout', methods=['POST'])
def checkout():
    """
    This API checkout for the order created by the user
    :return:
    """
    try:
        api_key = request.headers.get('Authorization')

        response = UserClient.get_user(api_key)

        if not response:
            return make_response(jsonify({'message': 'Not logged in'}), 401)

        user = response['result']

        order_model = Order.query.filter_by(user_id=user['id'], is_open=1).first()
        order_model.is_open = 0

        db.session.add(order_model)
        db.session.commit()

        response = jsonify({'result': order_model.to_json()})
    except CheckoutError as e:
        log.error(e)
        raise e
    return response
