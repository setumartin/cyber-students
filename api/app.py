from concurrent.futures import ThreadPoolExecutor
from motor import MotorClient
from tornado.web import Application

from .conf import MONGODB_HOST, MONGODB_DBNAME, WORKERS

from .handlers.welcome import WelcomeHandler
from .handlers.registration import RegistrationHandler
from .handlers.login import LoginHandler
from .handlers.logout import LogoutHandler
from .handlers.user import UserHandler

class Application(Application):

    def __init__(self):
        handlers = [
            (r'/students/?', WelcomeHandler),
            (r'/students/api/?', WelcomeHandler),
            (r'/students/api/registration', RegistrationHandler),
            (r'/students/api/login', LoginHandler),
            (r'/students/api/logout', LogoutHandler),
            (r'/students/api/user', UserHandler)
        ]

        settings = dict()

        super(Application, self).__init__(handlers, **settings)

        self.db = MotorClient(**MONGODB_HOST)[MONGODB_DBNAME]

        self.executor = ThreadPoolExecutor(WORKERS)
