from flask import Flask
from flask_restx import Api  # Swagger + Routing

# Blueprint routes
from app.routes.cookie_routes import cookie_routes, cookie_ns
from app.routes.order_routes import order_routes, order_ns

# Create the Swagger API object
api = Api(
    title="Cookie Shop API",
    version="1.0",
    description="Cookie Shop API Assessment"
)

def create_app():
    app = Flask(__name__)

    # Register Flask Blueprints
    app.register_blueprint(cookie_routes, url_prefix='/api')
    app.register_blueprint(order_routes, url_prefix='/api')

    # Attach namespaces (to Swagger only)
    api.init_app(app)
    api.add_namespace(cookie_ns, path='/api/cookies')
    api.add_namespace(order_ns, path='/api/orders')

    return app