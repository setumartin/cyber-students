from tornado.gen import coroutine
from tornado.web import authenticated

from .auth import AuthHandler

class LogoutHandler(AuthHandler):

    @authenticated
    @coroutine
    def post(self):
        yield self.db.users.update_one({
            'email': self.current_user['email'],
        }, {
            '$set': {
                'token': None
            }
        })

        self.current_user = None

        self.set_status(200)
        self.write_json()
