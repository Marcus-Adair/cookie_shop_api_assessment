'''
    Class to model an Order object
'''
from enum import Enum
from datetime import datetime


class Order:
    
    # Shared Class Variables
    _id_counter = 0  # Class-level counter to give orders unique IDs

    # Statuses for an order
    class OrderStatus(Enum):
        PENDING = 1
        DELIVERED = 2
        CANCELLED = 3  


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
            Convert the odrder object to a dictionary.
        """
        return {
            "id": self.id,
            "cookies_and_quantities": self.cookies_and_quantities,
            "order_date": self.order_date.isoformat() if isinstance(self.order_date, datetime) else self.order_date,
            "deliver_date": self.deliver_date.isoformat() if isinstance(self.deliver_date, datetime) else self.deliver_date,
            "status": self.status.name,
        }
    

    def __str__(self):
        """
        Return a string representation of the Order object.
        """
        return (f"Order(ID: {self.id}, "
                f"Cookies/Quantities: {self.cookies_and_quantities}, "
                f"Status: {self.status.name}, "
                f"Ordered: {self.order_date.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Deliver: {self.deliver_date.strftime('%Y-%m-%d %H:%M:%S')})")



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


    # TODO: Add method to calculate price of order (do get request to the cookies to get their prices )