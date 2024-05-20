import requests
import logging

log = logging.getLogger("frontend/ProductClient")
log.setLevel(logging.DEBUG)


class ProductClient:
    """
    A class for interacting with the Product API of the e-commerce backend.
    """

    @staticmethod
    def get_products():
        """
        Retrieves a list of available products from the Product API.

        Returns:
            A dictionary containing the product data on success, or an empty
            dictionary on error.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the Product API.
        """

        try:
            url = 'http://cproduct-service:5002/api/products'
            log.info(f"Retrieving products from: {url}")
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            products = response.json()
            return products
        except requests.exceptions.RequestException as e:
            log.error(f"Error retrieving products: {e}")
            return {}  # Return empty dictionary on error


    @staticmethod
    def get_product(slug):
        """
        Retrieves the details of a specific product by its slug from the
        Product API.

        Args:
            slug: The unique slug identifier for the product.

        Returns:
            A dictionary containing the product details on success, or an empty
            dictionary on error.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the Product API.
        """

        try:
            url = f'http://cproduct-service:5002/api/product/{slug}'
            log.info(f"Retrieving product details for slug: {slug} from: {url}")
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            product = response.json()
            return product
        except requests.exceptions.RequestException as e:
            log.error(f"Error retrieving product details for slug {slug}: {e}")
            return {}  # Return empty dictionary on error

