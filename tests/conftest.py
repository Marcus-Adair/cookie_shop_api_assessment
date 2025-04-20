# tests/conftest.py
import pytest
from flask import Flask
from flask_restx import Api
from app.routes.cookie_routes import cookie_routes, cookie_ns
from app.routes.order_routes import order_routes, order_ns

@pytest.fixture
def app():
    app = Flask(__name__)
    api = Api(app)

    api.add_namespace(cookie_ns)
    api.add_namespace(order_ns)

    app.register_blueprint(cookie_routes, url_prefix='/cookies')
    app.register_blueprint(order_routes, url_prefix='/orders')

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
