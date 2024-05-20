# application/product_api/routes.py
from . import product
from .. import db
from ..models import Product
from ..enums import ProductFetchingError, ProductAddingError, SlugError
from flask import jsonify, request
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@product.route('/api/products', methods=['GET'])
def products():
    """
    Retrieves all products.

    Returns:
        A JSON response containing a list of product details or an error message.

    Raises:
        ProductFetchingError: If there's an error fetching products from the database.
    """

    try:
        products = [product.to_json() for product in Product.query.all()]
        response = jsonify({'results': products})
    except Exception as e:
        log.error(f"Error fetching products: {e}")
        response = make_response(jsonify({'message': 'Internal server error'}), 500)
    return response


@product.route('/api/product/create', methods=['POST'])
def post_create():
    """
    Creates a new product.

    Returns:
        A JSON response containing a success message and the newly created product details
        or an error message.

    Raises:
        ProductAddingError: If there's an error creating the product in the database.
    """

    try:
        # Extract product details from request form
        name = request.form.get('name')
        slug = request.form.get('slug')
        image = request.form.get('image')
        price = request.form.get('price')

        # Validate required fields (consider adding more validation as needed)
        if not all([name, slug, image, price]):
            log.error("Missing required product details")
            raise ProductAddingError("Missing required fields")

        # Create a new Product object
        product = Product(name=name, slug=slug, image=image, price=price)

        # Save the product to the database
        db.session.add(product)
        db.session.commit()

        # Respond with success message and product details
        response = jsonify({
            'message': 'Product added successfully',
            'product': product.to_json()
        })
        log.info(f"Product created successfully: {product.name}")
    except ProductAddingError as e:
        log.error(e)
        raise e
    return response


@product.route('/api/product/<slug>', methods=['GET'])
def product(slug):
    """
    Retrieves a product by its slug.

    Args:
        slug: The unique slug of the product to retrieve.

    Returns:
        A JSON response containing the product details or an error message
        (404 Not Found).

    Raises:
        SlugError: If there's an error processing the slug.
    """

    try:
        # Find product by slug
        product = Product.query.filter_by(slug=slug).first()

        if product:
            # Product found, return details
            response = jsonify({'result': product.to_json()})
            log.info(f"Product retrieved successfully: {product.name}")
        else:
            # Product not found, return 404
            response = jsonify({'message': 'Product not found'}), 404
            log.info(f"Product not found with slug: {slug}")
    except SlugError as e:
        log.error(e)
        raise e
    return response

