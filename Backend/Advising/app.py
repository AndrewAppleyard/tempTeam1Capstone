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

app = create_app()

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        # Gunicorn
        # gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
        print("Production mode detected — run this app using Gunicorn.")
    else:
        # Flask
        app.run(debug=True, host="0.0.0.0", port=5000)