'''
    Class to model a Cookie object
'''
from typing import Optional

class Cookie:
    
    _id_counter = 0  # Class-level counter to give cookie unique IDs

    def __init__(self, name: str, description: str, price: float, inventory_count: int):

        '''
            Constructor for a new Cookie 
        '''

        # Validate inputs to new Cookie
        if not isinstance(name, str) or not name:
            raise ValueError("Cookie name must be a non-empty string.")
        
        if not isinstance(description, str) or not description:
            raise ValueError("Cookie description must be a non-empty string.")
        
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Cookie price must be a non-negative number.")
        
        if not isinstance(inventory_count, int) or inventory_count < 0:
            raise ValueError("Cookie inventory count must be a non-negative integer.")


        # Assign unique ID for new cookie product
        self.id = Cookie._id_counter
        Cookie._id_counter += 1 # Inc count for next Cookie


        # Cookie details
        self.name = name    # String
        self.description = description  # String
        self.price = round(price, 2)     # Float
        self.inventory_count = inventory_count   # Integer



    def to_dict(self):
        """
            Convert the cookie object to a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "inventory_count": self.inventory_count
        }
    

    # Setter Methods
    # ------------------------ #

    def set_name(self, name):
        if not isinstance(name, str):  # Name should be a string
            raise ValueError("Cookie ame must be a string.")

        if not name:  # Check if the name is not empty
            raise ValueError("Cookie name cannot be empty.")
        
        self.name = name

    def set_description(self, description):
        if not isinstance(description, str):
            raise ValueError("Cookie description must be a string.")
        
        self.description = description

    def set_price(self, price):
        if not isinstance(price, (int, float)):  # Price should be a number
            raise ValueError("Cookie price must be a number.")
        
        if price < 0:
            raise ValueError("Cookie price cannot be negative.")
        
        self.price = float(f"{price:.2f}") # Rount to 2 decimal points for cents

    def set_inventory_count(self, inventory_count):
        if not isinstance(inventory_count, int):  # Inventory should be an integer
            raise ValueError("Cookie inventory count must be an integer.")
        
        if inventory_count < 0:
            raise ValueError("Cookie inventory count cannot be negative.")
        
        self.inventory_count = inventory_count



    # Helper Methods: 
    # ------------------------ #



    def update_cookie(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        inventory_count: Optional[int] = None
    ):
        '''
            Update a cookies parameters. Optionally update parameters of choosing.
        '''

        updated = False

        if name:
            self.name = name
            updated = True
        if description:
            self.description = description
            updated = True
        if price is not None: 
            self.price = price
            updated = True
        if inventory_count is not None:
            self.inventory_count = inventory_count
            updated = True
        
        return updated




    def out_of_inventory(self):
        '''
            Returns False if the shop is out of this cookie and True if there are cookies
        '''
        return self.inventory_count == 0