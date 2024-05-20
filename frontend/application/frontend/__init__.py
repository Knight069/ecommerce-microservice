# application/frontend/__init__.py
from flask import Blueprint

frontend = Blueprint('frontend', __name__)

from . import views
