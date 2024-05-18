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
    This endpoint fetches all products
    :return:
    """
    try:
        items = []
        for row in Product.query.all():
            items.append(row.to_json())

        response = jsonify({'results': items})
    except ProductFetchingError as e:
        log.error(e)
        raise e
    return response


@product.route('/api/product/create', methods=['POST'])
def post_create():
    """
    This endpoint creates a new product
    :return:
    """
    try:
        name = request.form['name']
        slug = request.form['slug']
        image = request.form['image']
        price = request.form['price']

        item = Product()
        item.name = name
        item.slug = slug
        item.image = image
        item.price = price

        db.session.add(item)
        db.session.commit()

        response = jsonify({'message': 'Product added', 'product-service': item.to_json()})
        log.info(response)
    except ProductAddingError as e:
        log.error(e)
        raise e
    return response


@product.route('/api/product/<slug>', methods=['GET'])
def product(slug):
    """
    This endpoint fetches a product by slug
    :param slug:
    :return:
    """
    try:
        # fetching item by slug
        item = Product.query.filter_by(slug=slug).first()
        if item is not None:
            response = jsonify({'result': item.to_json()})
            log.info(response)
        else:
            response = jsonify({'message': 'Cannot find product'}), 404
            log.info(response)
    except SlugError as e:
        log.error(e)
        raise e
    return response
