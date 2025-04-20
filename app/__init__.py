from flask import Flask
from app.routes.cookie_routes import cookie_routes
from app.routes.order_routes import order_routes

def create_app():

    # Create the Flask application
    app = Flask(__name__)

    # Register blueprints for different routes
    app.register_blueprint(cookie_routes)
    app.register_blueprint(order_routes)

    return app