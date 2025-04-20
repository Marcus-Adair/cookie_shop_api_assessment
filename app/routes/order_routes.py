'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from datetime import datetime
from app.models.order import Order
from app.models.cookie import Cookie


# Create Blueprint
order_routes = Blueprint('order_routes', __name__)

# Create RESTX Namespace (for Swagger)
order_ns = Namespace('orders', description='Operations related to orders')


# In-memory storage for demo 
# ----------------------------------------------------------------- ##
orders = [] 

# Init some data to the storage
dt = datetime.fromisoformat('2025-01-20T15:30:00Z'.replace('Z', '+00:00'))
dt2 = datetime.fromisoformat('2025-02-02T15:30:00Z'.replace('Z', '+00:00'))
pending_status = Order.OrderStatus

order_1 = Order({1: 5}, dt, dt2, pending_status.PENDING)
orders.append(order_1)
# ----------------------------------------------------------------- ##


# DEFINE SCHEMA FOR VALIDATION 
# ----------------------------------------------------------------- ##

# Vars to reuse among models
cookies_and_quantities_description = 'Dictionary mapping cookie IDs (non-negative integers) to quantities (non-negative integers)'
cookies_and_quantities_example = {1: 12, 3: 5}


order_date_description = 'The datetime when the order was placed'
deliver_date_description = 'The datetime when the order should be delivered'
datetime_example = '2025-04-21T15:30:00Z'


status_description = 'The status of the order'
status_enum = ['PENDING', 'DELIVERED', 'CANCELLED']
status_example = 'PENDING'



# === Helper class to force input to be a dict that maps int --> int === #
class OrderDict(fields.Raw):
    def format(self, value):
        if not isinstance(value, dict):
            raise ValueError('Must be a dictionary')
        for k, v in value.items():
            if not isinstance(k, str) or not isinstance(v, int):
                raise ValueError('Keys must be strings and values must be integers')
        return value


# === Input Model for Creating an Order === #
order_input_model = order_ns.model('InputOrder', {
    'cookies_and_quantities': OrderDict(
        required=True,
        description=cookies_and_quantities_description,
        example=cookies_and_quantities_example
    ),
    'deliver_date': fields.DateTime(
        required=True,
        description=deliver_date_description,
        example=datetime_example
    ),
})

# === Output Model for an Order === #
order_output_model = order_ns.model('OuputOrder', {
    'id': fields.Integer(required=True, description='ID of the order'),
    'cookies_and_quantities': fields.Raw(
        required=True,
        description=cookies_and_quantities_description,
        example=cookies_and_quantities_example
    ),
    'order_date': fields.DateTime(
        required=True,
        description=order_date_description,
        example=datetime_example
    ),
    'deliver_date': fields.DateTime(
        required=True,
        description=deliver_date_description,
        example=datetime_example
    ),
    'status': fields.String(
        required=True,
        description=status_description,
        enum=status_enum,
        example=status_example
    ),
})

# ----------------------------------------------------------------- ##



@order_ns.route('/')
class OrderList(Resource):


    # TODO: add filter by date range 

    # TODO: add filter by total amount

    # GET /orders (list all orders or filter by status)
    @order_ns.marshal_list_with(order_output_model)
    @order_ns.doc(params={'status': f"Filter by order status. Options: {', '.join(status_enum)}"})
    def get(self):
        '''
        Get all orders, optionally filtered by status
        '''
        status = request.args.get('status', None)

        # TODO: add logic to filter by total amount and date too 


        if status:
            # Normalize and validate status input
            status = status.upper()
            if status not in status_enum:
                return {'message': f"Invalid status '{status}'. Must be one of {status_enum}"}, 400

            filtered_orders = [order.to_dict() for order in orders if order.status.name == status]
            return filtered_orders, 200

        # Return all orders if no filter is applied
        return [order.to_dict() for order in orders], 200






    # POST /orders (create an order given a list of product(s))
    @order_ns.expect(order_input_model, validate=True)
    @order_ns.marshal_with(order_output_model, code=201)
    def post(self):

        # Get data from the request body
        data = request.get_json()

        # Extract data from request (or get None)
        cookies_and_quantities = data.get('cookies_and_quantities')
        deliver_date = data.get('deliver_date')


        # Create valid format for Order constuctor from input JSON
        cookies_and_quantities_dict = {
            int(key): value
            for key, value in cookies_and_quantities.items()
        }
        deliver_date_datetime = datetime.fromisoformat(deliver_date.replace('Z', '+00:00'))
        order_status = Order.OrderStatus


        # TODO: make sure all of the IDs are valid by calling /cookies and checking IDs


        # Create a new Order instance 
        try:
            new_order = Order(cookies_and_quantities=cookies_and_quantities_dict, order_date=datetime.now(), deliver_date=deliver_date_datetime, status=order_status.PENDING)
        except ValueError as e:
            return {'message': str(e)}, 400  # Return the validation error from the Order constructor

        # Add the new order to the list
        orders.append(new_order)

        # Return the newly added order (Response code 201 for successful creation)
        return new_order.to_dict(), 201





@order_ns.route('/<int:id>')
@order_ns.param('id', 'The unique ID of the order')
class OrderByID(Resource):

    # GET /orders/<int:id>     (get specific order by id)
    @order_ns.response(200, 'Success', order_output_model)
    @order_ns.response(404, 'Order not found')
    def get(self, id):
        '''
        Get a single order by its ID
        '''
        for order in orders:
            if order.id == id:
                return order.to_dict(), 200
        
        # Return error message if order not found
        return {'message': f'Order with ID {id} not found'}, 404
    



    # TODO: add endpoint to update status by ID (with transition validation)

