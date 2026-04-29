from tornado.web import authenticated

from .auth import AuthHandler

class LogoutHandler(AuthHandler):

    @authenticated
    async def post(self):
        # Use the encrypted email from current_user
        await self.db.users.update_one({
            'email_encrypted': self.current_user['email_encrypted']
        }, {
            '$set': {
                'token': None
            }
        })

        self.current_user = None

        self.set_status(200)
        self.write_json()
