# application/product_api/__init__.py
from flask import Blueprint

product = Blueprint('product_api', __name__)

from . import routes
