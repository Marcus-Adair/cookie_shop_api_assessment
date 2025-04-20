'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, jsonify, request, current_app
from flask_restx import Namespace, Resource, fields
from datetime import datetime
from app.models.order import Order
from app.routes.cookie_routes import CookieByID
order_routes = Blueprint('order_routes', __name__) # Create Blueprint
order_ns = Namespace('orders', description='Operations related to orders') # Create RESTX Namespace (for Swagger)


# In-memory storage for demo 
# ----------------------------------------------------------------- ##
orders = [] 

# Init some mock data to the storage
dt = datetime.fromisoformat('2025-01-20T15:30:00Z'.replace('Z', '+00:00'))
dt2 = datetime.fromisoformat('2025-02-02T15:30:00Z'.replace('Z', '+00:00'))
pending_status = getattr(Order.OrderStatus, "PENDING")

order_1 = Order({1: 5, 0: 2}, dt, dt2, pending_status)
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
    ),
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
        status_search = request.args.get('status', None)
        min_total_amount = request.args.get('min_total_amount', type=float)
        max_total_amount = request.args.get('max_total_amount', type=float)
        min_date = request.args.get('min_date')
        max_date = request.args.get('max_date')
        if min_date:
            min_date = datetime.fromisoformat(min_date.replace('Z', '+00:00'))
        if max_date:
            max_date = datetime.fromisoformat(max_date.replace('Z', '+00:00'))


        filtered_orders = []

        for order in orders:

            # Filter by order status
            if status_search and status_search.upper() != order.status.name.upper():
                continue


            # Filter by the order date
            order_date = order.order_date # The date the order was made
            if min_date is not None and order_date < min_date:
                continue
            if max_date is not None and order_date > max_date:
                continue


            # If we want to filter by order's total amount
            total_amount = 0
            if min_total_amount or max_total_amount:

                # For each cookie-quantity combo in the order
                for cookie_id, cookie_quantity in order.cookies_and_quantities.items():

                    # Get the cookie details 
                    response_data, status_code = CookieByID().get(cookie_id)
                    if status_code == 200 and response_data:
                        cookie_price = response_data.get('price')
                        if cookie_price:

                            # Calculate order amount for current cookie
                            total_amount += (cookie_price * cookie_quantity) 

                    else:
                        print("No data or request failed when when getting cookie amounts")


            # Filter by the total cookie amount in the order
            if min_total_amount is not None and total_amount < min_total_amount:
                continue
            if max_total_amount is not None and total_amount > max_total_amount:
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
        cookies_and_quantities_dict = {
            int(key): value
            for key, value in cookies_and_quantities.items()
        }

        deliver_date_datetime = datetime.fromisoformat(deliver_date.replace('Z', '+00:00'))

        pending_status = getattr(Order.OrderStatus, "PENDING")


        # TODO: make sure all of the IDs are valid by calling /cookies and checking IDs


        # Create a new Order instance 
        try:
            new_order = Order(cookies_and_quantities=cookies_and_quantities_dict, order_date=datetime.now(), deliver_date=deliver_date_datetime, status=pending_status)
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
    


    # PATCH /orders/<int:id>    (update the status of an order)
    @order_ns.expect(order_patch_model, validate=True)
    @order_ns.response(200, 'Success', order_output_model)
    @order_ns.response(404, 'Order not found')
    def patch(self, id):
        '''
        Update an order's status by its ID
        '''


        # Get data from the request body
        data = request.get_json()

        if 'status' in data:

            # Map to define which state can transition to which
            valid_transitions = {
                "PENDING": ["COOKING", "CANCELLED"],
                "COOKING": ["SHIPPING", "CANCELLED"],
                "SHIPPING": ["DELIVERED", "CANCELLED"],
                "DELIVERED": [],
                "CANCELLED": []
            }

            # Find the order with the matching ID and save the index its at in the list
            order_to_update = None
            order_idx = 0
            for order in orders:
                if order.id == id:
                    order_to_update = order
                    break
                order_idx +=1

            if order_to_update is None:
                return {'message': f'order with ID {id} not found.'}, 404

            # Get status to try to transition to and the current status
            status_given = data['status'].upper() 
            current_status = order_to_update.status.name.upper()

            # Make sure requested status is valid
            if not hasattr(Order.OrderStatus, status_given):
                return {'message': f'The given status is not valid: {status_given}'}, 404

            # Validate status transition
            if status_given not in valid_transitions.get(current_status, []):
                return {'message': f'Cannot transition from {current_status} to {status_given}.'}, 400

            # Transition status
            new_status = getattr(Order.OrderStatus, status_given)
            order_to_update.set_status(new_status)

    
            # Update the orer
            orders[order_idx] = order_to_update

            return order_to_update.to_dict(), 200
        
        else:
            return {'message': 'No status to transistion to given'}, 404
    
