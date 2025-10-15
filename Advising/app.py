from flask import Flask, Blueprint, url_for
import os
import sys


from Advising.APIs import AdvisorAPI, AdminAPI, StudentAPI



def create_app():
    app = Flask(__name__, instance_relative_config=True)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(AdvisorAPI.bp)
    app.register_blueprint(AdminAPI.bp)
    app.register_blueprint(StudentAPI.bp)

    return app