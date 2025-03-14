from flask import Flask
from flask_jwt_extended import JWTManager
from routes.user_routes import user_bp
from routes.account_routes import account_bp
from routes.auth_routes import auth_bp
from routes.transaction_routes import transaction_bp
from utils.db import init_db

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"
app.config['DATABASE'] = 'instance/revobank.db'
jwt = JWTManager(app)

app.register_blueprint(user_bp)
app.register_blueprint(account_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(transaction_bp)

@app.before_request
def initialize_database():
    init_db()
    
if __name__ == "__main__":
    app.run(debug=True)
