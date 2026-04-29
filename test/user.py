from json import dumps
from tornado.escape import json_decode
from tornado.httputil import HTTPHeaders
from tornado.ioloop import IOLoop
from tornado.web import Application

from api.handlers.user import UserHandler
from api.security import hash_password, encrypt_field, hash_token, hash_email

from .base import BaseTest

class UserHandlerTest(BaseTest):

    @classmethod
    def setUpClass(self):
        self.my_app = Application([(r'/user', UserHandler)])
        super().setUpClass()

    async def register(self):
        # Hash email for lookup, encrypt displayName, hash password
        email_hash = hash_email(self.email)
        hashed_password = hash_password(self.password)
        encrypted_display_name = encrypt_field(self.display_name)
        
        await self.get_app().db.users.insert_one({
            'email': email_hash,
            'email_encrypted': encrypt_field(self.email),
            'password': hashed_password,
            'displayName': encrypted_display_name
        })

    async def login(self):
        # Hash the token for storage
        token_hash = hash_token(self.token)
        email_hash = hash_email(self.email)
        
        await self.get_app().db.users.update_one({
            'email': email_hash
        }, {
            '$set': { 'token': token_hash, 'expiresIn': 2147483647 }
        })

    def setUp(self):
        super().setUp()

        self.email = 'test@test.com'
        self.password = 'testPassword'
        self.display_name = 'testDisplayName'
        self.token = 'testToken'

        IOLoop.current().run_sync(self.register)
        IOLoop.current().run_sync(self.login)

    def test_user(self):
        headers = HTTPHeaders({'X-Token': self.token})

        response = self.fetch('/user', headers=headers)
        self.assertEqual(200, response.code)

        body_2 = json_decode(response.body)
        self.assertEqual(self.email, body_2['email'])
        self.assertEqual(self.display_name, body_2['displayName'])

    def test_user_without_token(self):
        response = self.fetch('/user')
        self.assertEqual(400, response.code)

    def test_user_wrong_token(self):
        headers = HTTPHeaders({'X-Token': 'wrongToken'})

        response = self.fetch('/user')
        self.assertEqual(400, response.code)
