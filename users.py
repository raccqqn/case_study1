class User:
    def __init__(self, id, name) -> None:
        """Create a new user based on the given name and id"""
        self.name = name
        self.id = id

    def store_data(self)-> None:
        """Save the user to the database"""
        pass

    def delete(self) -> None:
        """Delete the user from the database"""
        pass
    
    def __str__(self):
        return f"User {self.id} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def find_all(cls) -> list:
        """Find all users in the database"""
        pass

    @classmethod
    def find_by_attribute(cls, by_attribute : str, attribute_value : str) -> 'User':
        """From the matches in the database, select the user with the given attribute value"""
        pass
