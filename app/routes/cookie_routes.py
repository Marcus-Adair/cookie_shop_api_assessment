'''
    Cookie Routes - with Swagger Namespace
'''

from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.models.cookie import Cookie


# Create Blueprint
cookie_routes = Blueprint('cookie_routes', __name__)

# Create RESTX Namespace (for Swagger)
cookie_ns = Namespace('cookies', description='Operations related to cookies')


# In-memory storage for demo 
# ----------------------------------------------------------------- ##
cookies = [] 

# Init some data to the storage
cookie_1 = Cookie("Chocolate Chip", "A regular chocolate chip cookie", 1.00, 100)
cookie_2 = Cookie("Sugar Cookie", "A regular sugar cookie", 1.00, 1000)
cookies.append(cookie_1)
cookies.append(cookie_2)
# ----------------------------------------------------------------- ##



# DEFINE SCHEMA FOR VALIDATION 
# ----------------------------------------------------------------- ##

# Model for required input and types
cookie_input_model = cookie_ns.model('InputCookie', {
    'name': fields.String(required=True, description='Name of the cookie'),
    'description': fields.String(required=True, description='Cookie description'),
    'price': fields.Float(required=True, description='Price of the cookie'),
    'inventory_count': fields.Integer(required=True, description='Inventory count'),
})

# Swagger model for output
cookie_output_model = cookie_ns.model('OutputCookie', {
    'id': fields.Integer(required=True, description='ID of the cookie'),
    'name': fields.String(required=True, description='Name of the cookie'),
    'description': fields.String(required=True, description='Cookie description'),
    'price': fields.Float(required=True, description='Price of the cookie'),
    'inventory_count': fields.Integer(required=True, description='Inventory count'),
})


cookie_patch_model = cookie_ns.model('CookiePatch', {
    'name': fields.String(description='Name of the cookie'),
    'description': fields.String(description='Cookie description'),
    'price': fields.Float(description='Price of the cookie'),
    'inventory_count': fields.Integer(description='Inventory count'),
})

# ----------------------------------------------------------------- ##





@cookie_ns.route('/')
class CookieList(Resource):


    # GET /cookies (list all exisitng cookies)
    @cookie_ns.marshal_list_with(cookie_output_model)
    def get(self):
        '''
        Get all cookies in the shop
        '''

        # TODO: add pagination

        return [cookie.to_dict() for cookie in cookies]
    
    

    # POST /cookies (add a new cookie)
    @cookie_ns.expect(cookie_input_model, validate=True)
    @cookie_ns.marshal_with(cookie_output_model, code=201)
    def post(self):
        '''
        Add a new cookie to the shop
        '''

        # Get data from the request body
        data = request.get_json()

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

        # Add the new cookie to the list
        cookies.append(new_cookie)

        # Return the newly added cookie (Response code 201 for successful creation)
        return new_cookie.to_dict(), 201


    # TODO: add get_cookies_filter_name()    (search by specific name? or maybe close to?)    (with pagination!!)

    # TODO: add get_cookies_filter_price()   (two params for price ranging)      (with pagination!!)




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
        for cookie in cookies:
            if cookie.id == id:
                return cookie.to_dict(), 200
        
        # Return error message if cookie not found
        return {'message': f'Cookie with ID {id} not found'}, 404




    # PATCH /cookies/<int:id>    (partial (or full) update to a cookie)
    @cookie_ns.expect(cookie_patch_model, validate=True)
    @cookie_ns.response(200, 'Success', cookie_output_model)
    @cookie_ns.response(404, 'Cookie not found')
    def patch(self, id):
        '''
        Partially update a cookie by its ID
        '''

        # Get data from the request body
        data = request.get_json()

        cookie_to_update = None
        cookie_idx = 0

        # Find the cookie with the matching ID and save the index its at in the list
        for cookie in cookies:
            if cookie.id == id:
                cookie_to_update = cookie
                break
            cookie_idx +=1

        if cookie_to_update is None:
            return {'message': f'Cookie with ID {id} not found.'}, 404

        # Update only the fields present
        if 'name' in data:
            cookie_to_update.set_name(data['name'])
        if 'description' in data:
            cookie_to_update.set_description(data['description'])
        if 'price' in data:
            cookie_to_update.set_price(data['price'])
        if 'inventory_count' in data:
            cookie_to_update.set_inventory_count(data['inventory_count'])

        # Update the cookie
        cookies[cookie_idx] = cookie_to_update

        return cookie_to_update.to_dict(), 200



    # DELETE /cookies/<int:id>      (delete a specific cookie by its ID)
    @cookie_ns.response(204, 'Cookie deleted successfully')
    @cookie_ns.response(404, 'Cookie not found')
    def delete(self, id):
        '''
        Delete a cookie by its ID
        '''
        
        cookie_to_delete = None
        cookie_idx = 0

        # Find the cookie with the matching ID and save the index its at in the list
        for cookie in cookies:
            if cookie.id == id:
                cookie_to_delete = cookie
                break

            cookie_idx +=1

        if cookie_to_delete is None:
            return {'message': f'Cookie with ID {id} not found.'}, 404
        else:
            # Remove the cookie from the list
            cookies.pop(cookie_idx)

        # Return a 204 No Content response on success
        return '', 204
    
















