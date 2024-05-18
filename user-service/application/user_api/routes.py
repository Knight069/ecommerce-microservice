# application/user_api/routes.py
from imapclient.exceptions import LoginError

from . import user_api
from .. import db, login_manager
from ..models import User
from ..enums import UserCreationError, LoginError, LogoutError, UserNameError
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import logging
from passlib.hash import sha256_crypt

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@login_manager.user_loader
def load_user(user_id):
    """
    This method loads a user by ID.
    :param user_id:
    :return:
    """
    return User.query.filter_by(id=user_id).first()


@login_manager.request_loader
def load_user_from_request(request):
    """
    This method loads user from request.
    :param request:
    :return:
    """
    try:
        api_key = request.headers.get('Authorization')
        if api_key:
            log.debug("API key found")
            api_key = api_key.replace('Basic ', '', 1)
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                log.info("User found")
                return user
            else:
                log.info("User not found")
        else:
            log.warning("API key not found")
    except Exception as e:
        log.error(e)
        raise e
    return None


@user_api.route('/api/users', methods=['GET'])
def get_users():
    """
    This API returns a list of all users.
    :return:
    """
    try:
        data = []
        log.info("fetching list of all user")
        for row in User.query.all():
            data.append(row.to_json())

        response = jsonify(data)
        log.info("Details fetched successfully")
    except Exception as e:
        log.error(e)
        raise e
    return response


@user_api.route('/api/user/create', methods=['POST'])
def post_register():
    """
    This API creates a new user.
    :return:
    """
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']

        password = sha256_crypt.hash((str(request.form['password'])))

        user = User()
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.password = password
        user.username = username
        user.authenticated = True

        db.session.add(user)
        db.session.commit()

        response = jsonify({'message': 'User added', 'result': user.to_json()})
    except UserCreationError as e:
        log.error(e)
        raise e
    return response


@user_api.route('/api/user/login', methods=['POST'])
def post_login():
    """
    This API logs in a user.
    :return:
    """
    try:
        username = request.form['username']
        log.info(f"Loggin in user {username}")
        user = User.query.filter_by(username=username).first()
        if user:
            if sha256_crypt.verify(str(request.form['password']), user.password):
                user.encode_api_key()
                db.session.commit()
                login_user(user)
                log.info("User logged in")
                return make_response(jsonify({'message': 'Logged in', 'api_key': user.api_key}))
    except LoginError as e:
        log.error(e)
        raise e
    return make_response(jsonify({'message': 'Not logged in'}), 401)


@user_api.route('/api/user/logout', methods=['POST'])
def post_logout():
    """
    This API logs out a user.
    :return:
    """
    try:
        if current_user.is_authenticated:
            logout_user()
            log.info("User logged out")
            return make_response(jsonify({'message': 'You are logged out'}))
    except LogoutError as e:
        log.error(e)
        raise e
    log.warning("You are not logged in")
    return make_response(jsonify({'message': 'You are not logged in'}))


@user_api.route('/api/user/<username>/exists', methods=['GET'])
def get_username(username):
    """
    This API checks if the username exists.
    :param username:
    :return:
    """
    try:
        item = User.query.filter_by(username=username).first()
        if item is not None:
            log.info("User found")
            response = jsonify({'result': True})
        else:
            log.info("User not found")
            response = jsonify({'message': 'Cannot find username'}), 404
    except UserNameError as e:
        log.error(e)
        raise e
    return response


@login_required
@user_api.route('/api/user', methods=['GET'])
def get_user():
    """
    This API fetches details of current user.
    :return:
    """
    try:
        if current_user.is_authenticated:
            return make_response(jsonify({'result': current_user.to_json()}))
    except Exception as e:
        log.error(e)
        raise e
    return make_response(jsonify({'message': 'Not logged in'})), 401