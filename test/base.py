from concurrent.futures import ThreadPoolExecutor
from motor import MotorClient
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

from .conf import MONGODB_HOST, MONGODB_DBNAME, WORKERS

class BaseTest(AsyncHTTPTestCase):

    @classmethod
    def setUpClass(self):
        self.my_app.db = MotorClient(**MONGODB_HOST)[MONGODB_DBNAME]

        self.my_app.executor = ThreadPoolExecutor(WORKERS)

    def get_new_ioloop(self):
        return IOLoop.current()

    def get_app(self):
        return self.my_app

    def setUp(self):
        super().setUp()
        self.get_app().db.users.drop()

    def tearDown(self):
        super().tearDown()
        self.get_app().db.users.drop()
