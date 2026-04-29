from datetime import datetime, timezone

from ..security import hash_token, decrypt_field, hash_email
from .base import BaseHandler

class AuthHandler(BaseHandler):

    async def prepare(self):
        super(AuthHandler, self).prepare()

        if self.request.method == 'OPTIONS':
            return

        try:
            token = self.request.headers.get('X-Token')
            if not token:
              raise Exception()
        except Exception:
            self.current_user = None
            self.send_error(400, message='You must provide a token!')
            return

        # Hash the token for lookup
        token_hash = hash_token(token)
        
        user = await self.db.users.find_one({
            'token': token_hash
        }, {
            'email_encrypted': 1,
            'displayName': 1,
            'expiresIn': 1
        })

        if user is None:
            self.current_user = None
            self.send_error(403, message='Your token is invalid!')
            return

        current_time = datetime.now(timezone.utc).timestamp()
        if current_time > user['expiresIn']:
            self.current_user = None
            self.send_error(403, message='Your token has expired!')
            return

        # Decrypt email and displayName
        decrypted_email = decrypt_field(user['email_encrypted'])
        decrypted_display_name = decrypt_field(user['displayName'])

        # Store both decrypted and encrypted email for later use
        self.current_user = {
            'email': decrypted_email,
            'email_encrypted': user['email_encrypted'],
            'display_name': decrypted_display_name
        }
