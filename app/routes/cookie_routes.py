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



# Swagger model for input/output
cookie_model = cookie_ns.model('Cookie', {
    'name': fields.String(required=True, description='Name of the cookie'),
    'description': fields.String(required=True, description='Cookie description'),
    'price': fields.Float(required=True, description='Price of the cookie'),
    'inventory_count': fields.Integer(required=True, description='Inventory count'),
})



# GET /cookies (list all)
@cookie_ns.route('/')
class CookieList(Resource):
    @cookie_ns.marshal_list_with(cookie_model)
    def get(self):
        '''
            Get all cookies in the shop
        '''
        return [cookie.to_dict() for cookie in cookies]
    


# TODO add_cookie()

# TODO: add get_cookie_by_id()          (get single cookie by ID)

# TODO: add get_cookies_filter_name()    (search by specific name? or maybe close to?)

# TODO: add get_cookies_filter_price()   (two params for price ranging

# TODO: add update_cookie()         update exisitng cookie

# TODO: delete_cookie()         (delete by ID)