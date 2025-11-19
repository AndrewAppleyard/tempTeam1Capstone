from flask import Flask, Blueprint, url_for
from Advising.APIs import AdvisorAPI, AdminAPI, StudentAPI, TransferAPI, CurrentCourseAPI, AgentAPI, DegreePlanAPI, TranscriptAPI
from extensions import jwt
from flask_cors import CORS
import os
import sys
from datetime import timedelta
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

def create_app():

    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    CORS(app, resources = {r"/*": {
        "origins": "http://uafs_frontend:8080",
        "allow_headers": ["Authorization", "Content-Type", "X-CSRF-TOKEN"],
        "expose_headers": ["Authorization"],
        "methods" : ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    }})

    app.config["JWT_SECRET_KEY"] = "e90$2kj@#dju78)"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)

    app.config["JWT_COOKIE_SECURE"] = False
    app.config["JWT_COOKIE_SAMESITE"] = "None"

    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_CSRF_IN_COOKIES"] = True
    app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
    app.config["JWT_REFRESH_COOKIE_PATH"] = "/TransferAPI/refresh"
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    jwt.init_app(app)

    app.register_blueprint(TransferAPI.bp)
    app.register_blueprint(StudentAPI.bp)
    app.register_blueprint(AdvisorAPI.bp)
    app.register_blueprint(AdminAPI.bp)
    app.register_blueprint(CurrentCourseAPI.bp)
    app.register_blueprint(AgentAPI.bp)
    app.register_blueprint(DegreePlanAPI.bp)
    app.register_blueprint(TranscriptAPI.bp)

    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options():
        """ Handle OPTIONS requests for CORS preflight """
        response = Response()
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = 'http://uafs_frontend:8080'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-CSRF-TOKEN'
        return response

    return app

def runDev():
    app = create_app()

    app.run(host='0.0.0.0', port=5000)
