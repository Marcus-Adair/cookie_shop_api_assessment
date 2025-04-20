'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.models.order import Order
from app.models.cookie import Cookie


# Create Blueprint
order_routes = Blueprint('order_routes', __name__)

# Create RESTX Namespace (for Swagger)
order_ns = Namespace('orders', description='Operations related to orders')


# In-memory storage for demo 
# ----------------------------------------------------------------- ##
orders = [] 

# ----------------------------------------------------------------- ##


# Swagger model for input/output
order_model = order_ns.model('Order', {
    'name': fields.String(required=True, description='Name of the cookie'),
    'description': fields.String(required=True, description='Cookie description'),
    'price': fields.Float(required=True, description='Price of the cookie'),
    'inventory_count': fields.Integer(required=True, description='Inventory count'),
})



# GET /cookies (list all)
@order_ns.route('/')
class OrderList(Resource):
    @order_ns.marshal_list_with(order_model)
    def get(self):
        '''
            Get all orders in the shop
        '''
        return [order.to_dict() for order in orders]
    
