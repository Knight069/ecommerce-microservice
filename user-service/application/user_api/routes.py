# application/user_api/routes.py
from . import user_api
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .. import db, login_manager
from ..enums import UserCreationError, LoginError, LogoutError, UserNameError
from ..models import User
from passlib.hash import sha256_crypt
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user by ID from the database.

    Args:
        user_id: The user ID to load.

    Returns:
        The User object if found, otherwise None.
    """

    return User.query.filter_by(id=user_id).first()


@login_manager.request_loader
def load_user_from_request(request):
    """
    Attempts to load a user from the Authorization header in the request.

    Args:
        request: The Flask request object.

    Returns:
        The User object if found, otherwise None.
    """

    try:
        api_key = request.headers.get('Authorization')
        if api_key:
            log.debug("API key found in request header")
            api_key = api_key.replace('Basic ', '', 1)
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                log.info("User found by API key")
                return user
            else:
                log.info("User not found by API key")
    except Exception as e:
        log.error(e)
    return None


@user_api.route('/api/users', methods=['GET'])
def get_users():
    """
    Retrieves a list of all users.

    Restricted to administrators only (implement appropriate authorization checks).

    Returns:
        A JSON response containing a list of user details or an error message
        (401 Unauthorized).
    """

    # Implement authorization check for admins here (e.g., using a decorator)

    try:
        users = [user.to_json() for user in User.query.all()]
        response = jsonify(users)
        log.info("List of users fetched successfully")
    except Exception as e:
        log.error(e)
        response = make_response(jsonify({'message': 'Internal server error'}), 500)
    return response


@user_api.route('/api/user/create', methods=['POST'])
def post_register():
    """
    Creates a new user.

    Returns:
        A JSON response containing a success message and the newly created user details
        or an error message.

    Raises:
        UserCreationError: If there's an error creating the user in the database
        (e.g., username already exists).
    """

    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = sha256_crypt.hash(str(request.form['password']))

        user = User(email=email, first_name=first_name, last_name=last_name,
                    password=password, username=username)
        db.session.add(user)
        db.session.commit()

        response = jsonify({'message': 'User created successfully', 'result': user.to_json()})
        log.info(f"User created: {username}")
    except UserCreationError as e:
        log.error(e)
        raise e
    return response


@user_api.route('/api/user/login', methods=['POST'])
def post_login():
    """
    Logs in a user.

    Returns:
        A JSON response containing a success message and the API key or an error message
        (401 Unauthorized).
    """

    try:
        username = request.form['username']
        log.info(f"Login attempt for user {username}")
        user = User.query.filter_by(username=username).first()
        if user and sha256_crypt.verify(str(request.form['password']), user.password):
            user.encode_api_key()
            db.session.commit()
            login_user(user)
            log.info(f"User {username} logged in successfully")
            return make_response(jsonify({'message': 'Logged in', 'api_key': user.api_key}))
        else:
            log.info(f"Login failed for user {username}")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
    except LoginError as e:
        log.error(e)
        raise e


@user_api.route('/api/user/logout', methods=['POST'])
def post_logout():
    """
    Logs out the current user.

    Requires a valid user session (authenticated user).

    Returns:
        A JSON response containing a success message or an error message (401 Unauthorized).
    """

    try:
        if current_user.is_authenticated:
            logout_user()
            log.info(f"User {current_user.username} logged out")
            return make_response(jsonify({'message': 'You are logged out'}))
        else:
            log.info("User not logged in, cannot logout")
            return make_response(jsonify({'message': 'You are not logged in'}), 401)
    except LogoutError as e:
        log.error(e)
        raise e


@user_api.route('/api/user/<username>/exists', methods=['GET'])
def get_username(username):
    """
    Checks if a username exists.

    Returns:
        A JSON response indicating whether the username exists or an error message (404 Not Found).
    """

    try:
        user = User.query.filter_by(username=username).first()
        if user:
            log.info(f"Username {username} exists")
            response = jsonify({'result': True})
        else:
            log.info(f"Username {username} does not exist")
            response = jsonify({'message': 'Username not found'}), 404
    except UserNameError as e:
        log.error(e)
        raise e
    return response


@login_required
@user_api.route('/api/user', methods=['GET'])
def get_user():
    """
    Retrieves the details of the currently logged-in user.

    Requires a valid user session (authenticated user).

    Returns:
        A JSON response containing the user details or an error message (401 Unauthorized).
    """

    try:
        if current_user.is_authenticated:
            return make_response(jsonify({'result': current_user.to_json()}))
        else:
            log.info("User not logged in")
            return make_response(jsonify({'message': 'Not logged in'}), 401)
    except LoginError as e:
        log.error(e)
        raise e
