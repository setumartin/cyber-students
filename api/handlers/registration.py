from tornado.escape import json_decode

from ..security import hash_password, encrypt_field, hash_email
from .base import BaseHandler

class RegistrationHandler(BaseHandler):

    async def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            password = body['password']
            display_name = body.get('displayName')
            if display_name is None:
                display_name = email
            if not isinstance(display_name, str):
                raise Exception('Display name must be a string')
        except Exception:
            self.send_error(400, message='You must provide an email address, password and display name!')
            return

        if not email:
            self.send_error(400, message='The email address is invalid!')
            return

        if not password:
            self.send_error(400, message='The password is invalid!')
            return

        if not display_name:
            self.send_error(400, message='The display name is invalid!')
            return

        # Hash email for lookup, encrypt for storage
        email_hash = hash_email(email)
        encrypted_email = encrypt_field(email)
        
        user = await self.db.users.find_one({
          'email': email_hash
        })

        if user is not None:
            self.send_error(409, message='A user with the given email address already exists!')
            return

        # Hash the password
        hashed_password = hash_password(password)
        
        # Encrypt display name for storage
        encrypted_display_name = encrypt_field(display_name)

        await self.db.users.insert_one({
            'email': email_hash,
            'email_encrypted': encrypted_email,
            'password': hashed_password,
            'displayName': encrypted_display_name
        })

        self.set_status(200)
        self.response['email'] = email
        self.response['displayName'] = display_name

        self.write_json()
