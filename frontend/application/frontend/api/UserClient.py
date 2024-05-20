# application/frontend/api/UserClient.py
import requests
from flask import session, request
import logging

log = logging.getLogger("frontend/UserClient")
log.setLevel(logging.DEBUG)


class UserClient:
    """
    A class for interacting with the User API of the e-commerce backend.
    """

    @staticmethod
    def post_login(form):
        """
        Attempts to log in a user with the provided credentials and returns
        the API key on success.

        Args:
            form: A Flask-WTF form object containing username and password data.

        Returns:
            The user's API key on successful login, or None on failure.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the User API.
        """

        try:
            payload = {
                'username': form.username.data,
                'password': form.password.data
            }
            url = 'http://cuser-service:5001/api/user/login'
            response = requests.post(url, data=payload)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            data = response.json()
            if 'api_key' in data:
                return data['api_key']
            else:
                log.error("Login failed: Invalid credentials or missing API key in response.")
                return None

        except requests.exceptions.RequestException as e:
            log.error(f"Error logging in user: {e}")
            raise e

    @staticmethod
    def get_user():
        """
        Retrieves the currently logged-in user's details from the User API.

        Returns:
            A dictionary containing the user details on success, or an empty
            dictionary on error.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the User API.
        """

        try:
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            url = 'http://cuser-service:5001/api/user'
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            return response.json()

        except requests.exceptions.RequestException as e:
            log.error(f"Error retrieving user details: {e}")
            return {}

    @staticmethod
    def post_user_create(form):
        """
        Attempts to create a new user with the provided information.

        Args:
            form: A Flask-WTF form object containing user registration data.

        Returns:
            A dictionary containing the newly created user details on success,
            or None on failure.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the User API.
        """

        try:
            payload = {
                'email': form.email.data,
                'password': form.password.data,
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'username': form.username.data
            }
            url = 'http://cuser-service:5001/api/user/create'
            response = requests.post(url, data=payload)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            if response.status_code == 200:
                return response.json()
            else:
                log.error(f"User creation failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            log.error(f"Error creating user: {e}")
            raise e


    @staticmethod
    def does_exist(username):
        """
        Checks if a user with the given username already exists.

        Args:
            username: The username to check for existence.

        Returns:
            True if the username already exists, False otherwise.

        Raises:
            requests.exceptions.RequestException: If there's an error
                communicating with the User API.
        """

        try:
            url = f'http://cuser-service:5001/api/user/{username}/exists'
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            log.error(f"Error checking for username existence: {e}")
            return False

