from flask import Flask
from APIs.StudentAPI import bp as student_bp
from APIs.TransferAPI import bp as transfer_bp
from APIs.AdvisorAPI import bp as advisor_bp
from APIs.AdminAPI import bp as admin_bp
from APIs.CurrentCourseAPI import bp as current_course_bp
from extensions import jwt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "e90$2kj@#dju78)"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600

jwt.init_app(app)

app.register_blueprint(transfer_bp)
app.register_blueprint(student_bp)
app.register_blueprint(advisor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(current_course_bp)

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=5000, debug=True)
