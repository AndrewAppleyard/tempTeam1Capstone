from flask import Flask, Blueprint, url_for
from Advising.APIs import AdvisorAPI, AdminAPI, StudentAPI, TransferAPI
from extensions import jwt
from flask_cors import CORS
import os
import sys

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app)

    app.config["JWT_SECRET_KEY"] = "e90$2kj@#dju78)"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

    jwt.init_app(app)

    app.register_blueprint(TransferAPI.bp)
    app.register_blueprint(StudentAPI.bp)
    app.register_blueprint(AdvisorAPI.bp)
    app.register_blueprint(AdminAPI.bp)

    return app

def runDev():
    app = create_app()

    app.run(host='0.0.0.0', port=5000)
