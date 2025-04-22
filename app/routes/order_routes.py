'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from datetime import datetime
from app.models.order import Order
order_routes = Blueprint('order_routes', __name__) # Create Blueprint
order_ns = Namespace('orders', description='Operations related to orders') # Create RESTX Namespace
##############################################################################################################



# In-memory storage for demo 
# ----------------------------------------------------------------- ##
orders = {}     # Maps Order IDs to Order Objects

# Init some mock data to the storage
dt = datetime.fromisoformat('2025-01-20T15:30:00Z'.replace('Z', '+00:00'))
dt2 = datetime.fromisoformat('2025-02-02T15:30:00Z'.replace('Z', '+00:00'))
pending_status = getattr(Order.OrderStatus, "PENDING")

order_1 = Order({1: 5, 0: 2}, dt, dt2, pending_status)

orders[order_1.id] = order_1
# ----------------------------------------------------------------- ##


# DEFINE SCHEMA FOR VALIDATION 
# ----------------------------------------------------------------- ##

# Vars to reuse among models
cookies_and_quantities_description = 'Dictionary mapping cookie IDs (non-negative integers) to quantities (non-negative integers)'
cookies_and_quantities_example = {0: 12, 1: 5}


order_date_description = 'The datetime when the order was placed'
deliver_date_description = 'The datetime when the order should be delivered'
datetime_example = '2025-04-21T15:30:00Z'


status_description = 'The status of the order'
status_enum = ['PENDING', 'COOKING', 'SHIPPING', 'DELIVERED', 'CANCELLED']
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
    )
})


# === Model for Patching/Updating a Order === #
order_patch_model = order_ns.model('OrderPatch', {
    'status': fields.String(description=status_description, example=status_example),
})

# ----------------------------------------------------------------- ##



@order_ns.route('/')
class OrderList(Resource):


    # GET /orders (list all orders or filter by status)
    @order_ns.marshal_list_with(order_output_model)
    @order_ns.param('status', f"Filter by order status. Options: {', '.join(status_enum)}")
    @order_ns.param('min_total_amount', 'Filter by minimum total amount (float)', type='float')
    @order_ns.param('max_total_amount', 'Filter by maximum total amount (float)', type='float')
    @order_ns.param('min_date', 'Filter by minimum total amount (float)')
    @order_ns.param('max_date', 'Filter by maximum total amount (float)')
    def get(self):
        '''
        Get all orders, optionally filtered by status
        '''

        # Get search params
        status_search = request.args.get('status', type=str)
        min_total_amount = request.args.get('min_total_amount', type=float)
        max_total_amount = request.args.get('max_total_amount', type=float)
        min_date = request.args.get('min_date', type=str)
        max_date = request.args.get('max_date', type=str)
        if min_date:
            min_date = datetime.fromisoformat(min_date.replace('Z', '+00:00'))
        if max_date:
            max_date = datetime.fromisoformat(max_date.replace('Z', '+00:00'))


        filtered_orders = []

        for order in orders.values():

            # Filter by order status
            if status_search and status_search.upper() != order.status.name.upper():
                continue


            # Filter by the order date
            if min_date is not None and order.order_date < min_date:
                continue
            if max_date is not None and order.order_date > max_date:
                continue


            # Filter by price
            if min_total_amount or max_total_amount:

                total_order_amount = order.get_order_total_amount()

                # Filter by the total cookie amount in the order
                if min_total_amount is not None and total_order_amount < min_total_amount:
                    continue
                if max_total_amount is not None and total_order_amount > max_total_amount:
                    continue


            filtered_orders.append(order.to_dict()) # Add valid orders

        return filtered_orders, 200





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
        try:
            cookies_and_quantities_dict = {
                int(key): value
                for key, value in cookies_and_quantities.items()
            }
        except ValueError as e:
            return {'message': f"Error with cookie order: {str(e)}"}, 400 


        # TODO: make sure all of the IDs are valid by calling /cookies and checking IDs

        # New order made at current time
        deliver_date_datetime = datetime.fromisoformat(deliver_date.replace('Z', '+00:00'))

        # New order starts as PENDING
        pending_status = getattr(Order.OrderStatus, "PENDING")


        # Create a new Order instance 
        try:
            new_order = Order(cookies_and_quantities=cookies_and_quantities_dict, order_date=datetime.now(), deliver_date=deliver_date_datetime, status=pending_status)
        except ValueError as e:
            return {'message': f"Error creating cookie: {str(e)}"}, 400  # Return the validation error from the Order constructor

        # Add the new order to the list
        orders[new_order.id] = new_order

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
        if id in orders:
            return orders[id].to_dict(), 200
    
        else:
            return {'message': f'Order with ID {id} not found'}, 404




    # PATCH /orders/<int:id>    (update the status of an order)
    @order_ns.expect(order_patch_model, validate=True)
    @order_ns.response(200, 'Success', order_output_model)
    @order_ns.response(400, 'Invalid input data')
    @order_ns.response(404, 'Order not found')
    def patch(self, id):
        '''
        Update an order's status by its ID
        '''

        # Map to define which state can transition to which
        valid_transitions = {
            "PENDING": ["COOKING", "CANCELLED"],
            "COOKING": ["SHIPPING", "CANCELLED"],
            "SHIPPING": ["DELIVERED", "CANCELLED"],
            "DELIVERED": [],
            "CANCELLED": []
        }


        # Get data from the request body
        data = request.get_json()
        if data is None:
            return {'message': 'Invalid or missing JSON in request body'}, 400
        status_given = data.get('status')
            

        if status_given:
            if id in orders:

                status_given = status_given.upper()
                current_status = orders[id].status.name.upper()

                # Make sure requested status is valid
                if not hasattr(Order.OrderStatus, status_given):
                    return {'message': f'The given status is not valid: {status_given}'}, 404

                # Validate status transition
                if status_given not in valid_transitions.get(current_status, []):
                    return {'message': f'Cannot transition from {current_status} to {status_given}.'}, 400

                # Transition status
                orders[id].set_status(getattr(Order.OrderStatus, status_given))

                # Return updated order
                return orders[id].to_dict(), 200


            else:
                return {'message': f'order with ID {id} not found.'}, 404
        else:
            return {'message': 'No status to transistion to given'}, 404
    
