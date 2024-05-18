# application/frontend/api/OrderClient.py
from flask import session
import requests
import logging
from ..enums import GetOrderError, CartError, CheckOurError

log = logging.getLogger("frontend/OrderClient")
log.setLevel(logging.DEBUG)


class OrderClient:
    @staticmethod
    def get_order():
        """
        This method fetches all orders
        :return:
        """
        try:
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            url = 'http://corder-service:5003/api/order'
            log.info(f"Retrieving orders with api: {url}")
            response = requests.request(method="GET", url=url, headers=headers)
            log.debug(f"Order response code: {response.status_code}")
            order = response.json()
        except GetOrderError as e:
            log.error(e)
            raise e
        return order

    @staticmethod
    def post_add_to_cart(product_id, qty=1):
        """
        This method adds a product to the cart
        :param product_id:
        :param qty:
        :return:
        """
        try:
            payload = {
                'product_id': product_id,
                'qty': qty
            }
            url = 'http://corder-service:5003/api/order/add-item'
            log.info(f"Adding product to cart with: {url} and product: {payload}")
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            response = requests.request("POST", url=url, data=payload, headers=headers)
            if response.status_code == 200:
                order = response.json()
                return order
            else:
                raise CartError
        except CartError as e:
            log.error(e)
            raise e

    @staticmethod
    def post_checkout():
        """
        This method checks out the cart
        :return:
        """
        try:
            url = 'http://corder-service:5003/api/order/checkout'

            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            response = requests.request("POST", url=url, headers=headers)
            log.debug(f"Checkout response code: {response.status_code}")
            order = response.json()
        except CheckOurError as e:
            log.error(e)
            raise e
        return order

    @staticmethod
    def get_order_from_session():
        default_order = {
            'items': {},
            'total': 0,
        }
        return session.get('order', default_order)
