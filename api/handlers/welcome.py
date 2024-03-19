from .base import BaseHandler

class WelcomeHandler(BaseHandler):

    def get(self):
        self.set_status(200)
        self.response['message'] = 'Welcome to the Cyber Students Server!';
        self.write_json()
