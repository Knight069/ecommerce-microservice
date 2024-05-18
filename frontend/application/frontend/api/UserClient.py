# application/frontend/api/UserClient.py
import requests
from flask import session, request
import logging

log = logging.getLogger("frontend/ProductClient")
log.setLevel(logging.DEBUG)


class UserClient:
    @staticmethod
    def post_login(form):
        """
        This method return API key after login
        :param form:
        :return: api key
        """
        try:
            api_key = False
            payload = {
                'username': form.username.data,
                'password': form.password.data
            }
            url = 'http://cuser-service:5001/api/user/login'
            response = requests.request("POST", url=url, data=payload)
            if response.status_code == 200:
                d = response.json()
                print("This is response from user api: " + str(d))
                if d['api_key'] is not None:
                    api_key = d['api_key']
            return api_key
        except Exception as ex:
            log.error(ex)
            raise ex

    @staticmethod
    def get_user():
        """
        This method returns user details
        :return:
        """
        try:
            headers = {
                'Authorization': 'Basic ' + session['user_api_key']
            }
            url = 'http://cuser-service:5001/api/user'
            response = requests.request(method="GET", url=url, headers=headers)
            user = response.json()
            log.info("This is response from user api: " + str(user))
            return user
        except Exception as ex:
            log.error(ex)
            raise ex


    @staticmethod
    def post_user_create(form):
        """
        This method returns user details after user creation
        :param form:
        :return:
        """
        try:
            log.info("Starting user creation")
            user = False
            payload = {
                'email': form.email.data,
                'password': form.password.data,
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'username': form.username.data
            }
            url = 'http://cuser-service:5001/api/user/create'
            response = requests.request("POST", url=url, data=payload)
            if response.status_code == 200:
                log.info("User created successfully")
                user = response.json()
            return user
        except Exception as ex:
            log.error(ex)
            raise ex

    @staticmethod
    def does_exist(username):
        url = 'http://cuser-service:5001/api/user/' + username + '/exists'
        response = requests.request("GET", url=url)
        return response.status_code == 200

