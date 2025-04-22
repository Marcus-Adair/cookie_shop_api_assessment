'''
    Class to model an Order object
'''
from enum import Enum
from datetime import datetime
from app.routes.cookie_routes import CookieByID
from app.models.cookie import Cookie


class Order:
    
    _id_counter = 0  # Class-level counter to give orders unique IDs

    # Statuses for an order
    class OrderStatus(Enum):
        PENDING = 1
        COOKING = 2
        SHIPPING = 3
        DELIVERED = 4
        CANCELLED = 5  


    def __init__(self, cookies_and_quantities: dict, order_date: datetime, deliver_date: datetime, status: OrderStatus):

        '''
            Constructor for a new Order 
        '''

        # Validate inputs to new Order
        if not isinstance(cookies_and_quantities, dict):  # Validate it's a dictionary
            raise ValueError(f"cookies_and_quantities must be a dictionary, got {type(cookies_and_quantities)} instead.")

        # Check that k-v pairs are valid in cookies/quantities dict
        for key, value in cookies_and_quantities.items():
            if not isinstance(key, int) or key < 0:
                raise ValueError(f"Each key value must be a non-negative integer. Found {key}.")
            
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"Each quantity value must be a non-negative integer. Found {value} for cookie ID {key}.")
            
        if not isinstance(order_date, datetime):  # Ensure it's a datetime object
            raise ValueError(f"order_date must be a datetime object, got {type(order_date)} instead.")

        if not isinstance(deliver_date, datetime):  # Ensure it's a datetime object
            raise ValueError(f"deliver_date must be a datetime object, got {type(deliver_date)} instead.")

        if not isinstance(status, Order.OrderStatus):  # Ensure it's an instance of OrderStatus Enum
            raise ValueError(f"status must be an instance of OrderStatus Enum, got {type(status)} instead.")


        # Assign unique ID for new cookie product
        self.id = Order._id_counter
        Order._id_counter += 1 # Inc counter for next order

        self.cookies_and_quantities = cookies_and_quantities    # Map (Cookie ID --> Number)
        self.order_date = order_date    # Datetime
        self.deliver_date = deliver_date    # Datetime
        self.status = status    # An instance of OrderStatus Enum


    def to_dict(self):
        """
            Convert the order object to a dictionary.
        """
        return {
            "id": self.id,
            "cookies_and_quantities": self.cookies_and_quantities,
            "order_date": self.order_date.isoformat() if isinstance(self.order_date, datetime) else self.order_date,
            "deliver_date": self.deliver_date.isoformat() if isinstance(self.deliver_date, datetime) else self.deliver_date,
            "status": self.status.name,
        }
    


    # Setter Methods
    # ------------------------ #

    def set_cookies_and_quantities(self, cookies_and_quantities):
        if isinstance(cookies_and_quantities, dict):  # Validate it's a dictionary
            self.cookies_and_quantities = cookies_and_quantities
        else:
            raise ValueError(f"cookies_and_quantities must be a dictionary, got {type(cookies_and_quantities)} instead.")


    def set_cookies_and_quantities(self, cookies_and_quantities):
        if isinstance(cookies_and_quantities, dict):  # Validate it's a dictionary

            # Check that k-v pairs are valid
            for key, value in cookies_and_quantities.items():
                if not isinstance(key, int) or key < 0:
                    raise ValueError(f"Each key value must be a non-negative integer. Found {key}.")
                
                if not isinstance(value, int) or value < 0:
                    raise ValueError(f"Each quantity value must be a non-negative integer. Found {value} for cookie ID {key}.")
                
            self.cookies_and_quantities = cookies_and_quantities
        else:
            raise ValueError(f"cookies_and_quantities must be a dictionary, got {type(cookies_and_quantities)} instead.")


    def set_order_date(self, order_date):
        if isinstance(order_date, datetime):  # Ensure it's a datetime object
            self.order_date = order_date
        else:
            raise ValueError(f"order_date must be a datetime object, got {type(order_date)} instead.")

    def set_deliver_date(self, deliver_date):
        if isinstance(deliver_date, datetime):  # Ensure it's a datetime object
            self.deliver_date = deliver_date
        else:
            raise ValueError(f"deliver_date must be a datetime object, got {type(deliver_date)} instead.")

    def set_status(self, status):
        if isinstance(status, Order.OrderStatus):  # Ensure it's an instance of OrderStatus Enum
            self.status = status
        else:
            raise ValueError(f"status must be an instance of OrderStatus Enum, got {type(status)} instead.")



    # Helper Methods: 
    # ------------------------ #

    def get_order_total_amount(self):
        '''
        Calculate the total price of an order.
        '''
        order_total_amount = 0

        for cookie_id, cookie_quantity in self.cookies_and_quantities.items():

            # Get the 
            response_data, status_code = CookieByID().get(cookie_id)
            if status_code == 200 and response_data:
                try:
                    cookie = Cookie(
                        name=response_data['name'],
                        description=response_data['description'],
                        price=response_data['price'],
                        inventory_count=response_data['inventory_count']
                    )

                    # Add to total
                    order_total_amount += (cookie.price * cookie_quantity)

                except Exception as e:
                    print(f"Error creating Cookie (id:{cookie_id}) object: {e}")

            else:
                print(f"No data or request failed when getting Cookie (id:{cookie_id}) details.")

        return round(order_total_amount, 2)