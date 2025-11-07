import multiprocessing

from gunicorn.app.wsgiapp import WSGIApplication
from Advising import app
from app import create_app

app = create_app()

class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


def run():
    options = {
        "bind": "0.0.0.0:5000",
        "workers": (multiprocessing.cpu_count() * 2) + 1
    }
    StandaloneApplication("wsgi:app", options).run()