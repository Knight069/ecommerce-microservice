# application/frontend/api/ProductClient.py
import requests
import logging

log = logging.getLogger("frontend/ProductClient")
log.setLevel(logging.DEBUG)


class ProductClient:

    @staticmethod
    def get_products():
        """
        This method fetches the products.
        :return: products
        """
        try:
            r = requests.get('http://cproduct-service:5002/api/products')
            products = r.json()
        except Exception as e:
            log.error(e)
            raise e
        return products

    @staticmethod
    def get_product(slug):
        """
        This method fetches the product details.
        :param slug:
        :return: product json
        """
        try:
            response = requests.request(method="GET", url='http://cproduct-service:5002/api/product/' + slug)
            product = response.json()
        except Exception as e:
            log.error(e)
            raise e
        return product
