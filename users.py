import os
from tinydb import TinyDB, Query
from serializer import serializer


class User:
    # eigene Tabelle „users“
    db_connector = TinyDB(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'),
        storage=serializer
    ).table('users')

    def __init__(self, id: str, name: str) -> None:
        """
        id = Mailadresse (unique)
        name = Anzeigename
        """
        self.id = id
        self.name = name

    def store_data(self) -> None:
        """Insert or Update user"""
        UserQuery = Query()
        result = User.db_connector.search(UserQuery.id == self.id)

        if result:
            User.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
        else:
            User.db_connector.insert(self.__dict__)

    def delete(self) -> None:
        """Delete user"""
        UserQuery = Query()
        result = User.db_connector.search(UserQuery.id == self.id)

        if result:
            User.db_connector.remove(doc_ids=[result[0].doc_id])

    def __str__(self):
        return f"User {self.id} - {self.name}"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def find_all(cls) -> list:
        """Returns list[User]"""
        users = []
        for u in cls.db_connector.all():
            users.append(User(u["id"], u["name"]))
        return users

    @classmethod
    def find_by_attribute(cls, by_attribute: str, attribute_value: str):
        """Returns first match or None"""
        UserQuery = Query()
        result = cls.db_connector.search(UserQuery[by_attribute] == attribute_value)

        if not result:
            return None

        u = result[0]
        return User(u["id"], u["name"])
