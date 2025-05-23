'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.models.cookie import Cookie
cookie_routes = Blueprint('cookie_routes', __name__) # Create Blueprint
cookie_ns = Namespace('cookies', description='Operations related to cookies') # Create RESTX Namespace
##############################################################################################################



# In-memory storage for demo 
# ----------------------------------------------------------------- ##
cookies = {}    # Maps Cookie IDs to Cookie objects

# Init some mock data to the storage
cookie_1 = Cookie("Chocolate Chip", "A regular chocolate chip cookie", 2.99, 100)
cookie_2 = Cookie("Sugar Cookie", "A regular sugar cookie", 1.50, 1000)


cookies[cookie_1.id] = cookie_1
cookies[cookie_2.id] = cookie_2
# ----------------------------------------------------------------- ##



# DEFINE SCHEMA FOR VALIDATION 
# ----------------------------------------------------------------- ##

name_description = 'Name of the cookie'
name_example = "Sugar Cookie"

description_description = 'Cookie description'
description_example = "A cookie made out of sugar"

price_description = 'Price of the cookie'
price_example = 1.99

inventory_description = 'Inventory count'
inventory_example = 10

# === Input Model for Creating a Cookie === #
cookie_input_model = cookie_ns.model('InputCookie', {
    'name': fields.String(required=True, description=name_description, example=name_example),
    'description': fields.String(required=True, description=description_description, example=description_example),
    'price': fields.Float(required=True, description=price_description, example=price_example),
    'inventory_count': fields.Integer(required=True, description=inventory_description, example=inventory_example),
})

# === Model for Patching/Updating a Cookie === #
cookie_patch_model = cookie_ns.model('CookiePatch', {
    'name': fields.String(description=name_description, example=name_example),
    'description': fields.String(description=description_description, example=description_example),
    'price': fields.Float(description=price_description, example=price_example),
    'inventory_count': fields.Integer(description=inventory_description, example=inventory_example),
})

# === Output Model for Cookie === #
cookie_output_model = cookie_ns.model('OutputCookie', {
    'id': fields.Integer(required=True, description='ID of the cookie'),
    'name': fields.String(required=True, description=name_description, example=name_example),
    'description': fields.String(required=True, description=description_description, example=description_example),
    'price': fields.Float(required=True, description=price_description, example=price_example),
    'inventory_count': fields.Integer(required=True, description=inventory_description, example=inventory_example),
})

# ----------------------------------------------------------------- ##



@cookie_ns.route('/')
class CookieList(Resource):


    # GET /cookies (list all exisitng cookies)
    @cookie_ns.response(200, 'Success', cookie_output_model)
    @cookie_ns.param('name_search', "Filter by order name.")
    @cookie_ns.param('min_price', 'Filter by minimum price (float)', type='float')
    @cookie_ns.param('max_price', 'Filter by maximum price (float)', type='float')
    @cookie_ns.param('page', 'Page number (starting from 1)', type='int')
    @cookie_ns.param('per_page', 'Number of cookies per page', type='int')
    @cookie_ns.response(400, 'Invalid input data')
    def get(self):
        '''
        Get all cookies in the shop, optionally filtered by name
        '''

        # Get filter parameters or None
        name_search = request.args.get('name_search', type=str)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # Pagination
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)


        filtered_cookies = []
        for cookie in cookies.values():

            # Only apply filter if it was provided
            if name_search and name_search.lower() not in cookie.name.lower():
                continue
            if min_price is not None and cookie.price < min_price:
                continue
            if max_price is not None and cookie.price > max_price:
                continue

            # Add cookie if it passes all the filter
            filtered_cookies.append(cookie.to_dict())


        # Apply pagination
        if page and per_page:
            if page < 1 or per_page < 1:
                return {'message': 'page and per_page must be positive integers'}, 400

            start = (page - 1) * per_page # idx of start cookie
            end = start + per_page # idx of end cookie

            # Build the requested page
            paginated_cookies = filtered_cookies[start:end]
            return paginated_cookies, 200

        # No pagination if not requested
        else:
            return filtered_cookies, 200
    
    

    # POST /cookies (add a new cookie)
    @cookie_ns.expect(cookie_input_model, validate=True)
    @cookie_ns.marshal_with(cookie_output_model, code=201)
    @cookie_ns.response(400, 'Invalid input data')
    def post(self):
        '''
        Add a new cookie to the shop
        '''

        # Get data from the request body
        data = request.get_json()
        if data is None:
            return {'message': 'Invalid or missing JSON in request body'}, 400


        # Extract data from request (or get None)
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        inventory_count = data.get('inventory_count')

        # Create a new Cookie instance
        try:
            new_cookie = Cookie(name=name, description=description, price=price, inventory_count=inventory_count)
        except ValueError as e:
            return {'message': str(e)}, 400  # Return the validation error from the Cookie constructor

        # Add the new cookie
        cookies[new_cookie.id] = new_cookie

        # Return the newly added cookie
        return new_cookie.to_dict(), 201



# Order Endpoint using IDs
@cookie_ns.route('/<int:id>')
@cookie_ns.param('id', 'The unique ID of the cookie')
class CookieByID(Resource):

    # GET /cookies/<int:id>     (get specific cookie by id)
    @cookie_ns.response(200, 'Success', cookie_output_model)
    @cookie_ns.response(404, 'Cookie not found')
    def get(self, id):
        '''
        Get a single cookie by its ID
        '''

        if id in cookies:
            return cookies[id].to_dict(), 200

        else:
            return {'message': f'Cookie with ID {id} not found'}, 404





    # PATCH /cookies/<int:id>    (partial (or fully) update a cookie)
    @cookie_ns.expect(cookie_patch_model, validate=True)
    @cookie_ns.response(200, 'Success', cookie_output_model)
    @cookie_ns.response(400, 'Invalid input data')
    @cookie_ns.response(404, 'Cookie not found')
    def patch(self, id):
        '''
        Update a cookie by its ID
        '''

        # Get data from the request body
        data = request.get_json()
        if data is None:
            return {'message': 'Invalid or missing JSON in request body'}, 400

        # See if the cookie exists 
        if id in cookies:

            # Extract data from request (or get None)
            name = data.get('name')
            description = data.get('description')
            price = data.get('price')
            inventory_count = data.get('inventory_count')

            # Update the cookie's details
            updated = cookies[id].update_cookie(name, description, price, inventory_count)

            # Return updated cookie
            if updated:
                return cookies[id].to_dict(), 200
            else:
                return {'message': 'Invalid or missing JSON in request body'}, 400

        else:
            return {'message': f'Cookie with ID {id} not found.'}, 404







    # DELETE /cookies/<int:id>      (delete a specific cookie by its ID)
    @cookie_ns.response(204, 'Cookie deleted successfully')
    @cookie_ns.response(404, 'Cookie not found')
    def delete(self, id):
        '''
        Delete a cookie by its ID
        '''

        # See if the cookie exists 
        if id in cookies:
            del cookies[id]

            # Return a 204 No Content response on success
            return '', 204

        else:
            return {'message': f'Cookie with ID {id} not found.'}, 404      





    
















