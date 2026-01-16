from typing import Self
from datetime import datetime

from serializable import Serializable
from database import DatabaseConnector

class User(Serializable):

    db_connector =  DatabaseConnector().get_table("users")

    def __init__(self, id : str , name : str, creation_date: datetime = None, last_update: datetime = None) -> None:
        super().__init__(id, creation_date, last_update)
        self.name = name

    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(data['id'], data['name'], data['creation_date'], data['last_update'])

    def __str__(self):
        return f"User: {self.name} ({self.id})"

if __name__ == "__main__":
    # Create a device
    user1 = User("one@mci.edu", "User One",)
    user2 = User("two@mci.edu", "User Two", ) 
    user3 = User( "three@mci.edu", "User Three") 
    user1.store_data()
    user2.store_data()
    user3.store_data()
    user4 = User("User Four", "four@mci.edu") 
    user4.store_data()

    loaded_user = User.find_by_attribute("id", "one@mci.edu")
    if loaded_user:
        print(f"Loaded: {loaded_user}")
    else:
        print("User not found.")

    all_users = User.find_all()
    for user in all_users:
        print(user)