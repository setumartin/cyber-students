from datetime import datetime, timedelta, timezone
from tornado.escape import json_decode
from uuid import uuid4

from ..security import encrypt_field, verify_password, hash_token, hash_email
from .base import BaseHandler

class LoginHandler(BaseHandler):

    async def generate_token(self, email):
        token_uuid = uuid4().hex
        expires_in = (datetime.now(timezone.utc) + timedelta(hours=2)).timestamp()

        # Hash the token for storage
        token_hash = hash_token(token_uuid)
        
        # Hash email for lookup
        email_hash = hash_email(email)

        token = {
            'token': token_hash,
            'expiresIn': expires_in,
        }

        await self.db.users.update_one({
            'email': email_hash
        }, {
            '$set': token
        })

        return {
            'token': token_uuid,
            'expiresIn': expires_in,
        }

    async def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            password = body['password']
        except Exception:
            self.send_error(400, message='You must provide an email address and password!')
            return

        if not email:
            self.send_error(400, message='The email address is invalid!')
            return

        if not password:
            self.send_error(400, message='The password is invalid!')
            return

        # Hash email for lookup
        email_hash = hash_email(email)
        
        user = await self.db.users.find_one({
          'email': email_hash
        }, {
          'password': 1
        })

        if user is None:
            self.send_error(403, message='The email address and password are invalid!')
            return

        if not verify_password(password, user['password']):
            self.send_error(403, message='The email address and password are invalid!')
            return

        token = await self.generate_token(email)

        self.set_status(200)
        self.response['token'] = token['token']
        self.response['expiresIn'] = token['expiresIn']

        self.write_json()
