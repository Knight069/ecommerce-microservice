# application/frontend/api/OrderClient.py
from flask import session
import requests
import logging

from ..enums import GetOrderError, CartError, CheckoutError  # Assuming enums are defined elsewhere

log = logging.getLogger("frontend/OrderClient")
log.setLevel(logging.DEBUG)


class OrderClient:
    """
    A class for interacting with the Order API of the e-commerce backend.
    """

    @staticmethod
    def get_order():
        """
        Retrieves the current user's order details from the Order API.

        Returns:
            A dictionary containing the order details or an empty dictionary
            on error.

        Raises:
            GetOrderError: If there's an error fetching the order.
        """

        try:
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            url = 'http://corder-service:5003/api/order'
            log.info(f"Retrieving orders with API: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            order = response.json()
            return order
        except requests.exceptions.RequestException as e:
            log.error(f"Error retrieving order: {e}")
            raise GetOrderError("An error occurred while fetching your order.") from e

    @staticmethod
    def post_add_to_cart(product_id, qty=1):
        """
        Adds a product to the user's cart in the Order API.

        Args:
            product_id: The ID of the product to add.
            qty: The quantity of the product to add (default: 1).

        Returns:
            A dictionary containing the updated order details on success.

        Raises:
            CartError: If there's an error adding the product to the cart.
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
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            order = response.json()
            return order
        except requests.exceptions.RequestException as e:
            log.error(f"Error adding product to cart: {e}")
            raise CartError("An error occurred while adding the product to your cart.") from e

    @staticmethod
    def post_checkout():
        """
        Processes the checkout for the user's current order in the Order API.

        Returns:
            A dictionary containing the checkout details on success.

        Raises:
            CheckoutError: If there's an error processing the checkout.
        """

        try:
            url = 'http://corder-service:5003/api/order/checkout'
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            order = response.json()
            return order
        except requests.exceptions.RequestException as e:
            log.error(f"Error processing checkout: {e}")
            raise CheckoutError("An error occurred while processing your checkout.") from e

    @staticmethod
    def get_order_from_session():
        """
        Retrieves the order data stored in the user session.

        Returns:
            A dictionary containing the order data or an empty dictionary
            if no order is found in the session.
        """

        default_order = {
            'items': {},
            'total': 0,
        }
        return session.get('order', default_order)