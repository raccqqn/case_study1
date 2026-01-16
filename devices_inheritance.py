from typing import Self
from datetime import datetime
import uuid

from serializable import Serializable
from database import DatabaseConnector


class Device(Serializable):

    db_connector = DatabaseConnector().get_table("devices")

    def __init__(
        self,
        device_name: str,
        device_type: str,
        count: int,
        managed_by_user_id: str,
        id: str | None = None,
        creation_date: datetime = None,
        last_update: datetime = None,
    ):
        # Wenn keine ID übergeben wird → neue UUID
        if id is None:
            id = str(uuid.uuid4())

        super().__init__(id, creation_date, last_update)

        self.device_name = device_name
        self.device_type = device_type
        self.count = count
        self.managed_by_user_id = managed_by_user_id

    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:
        return cls(
            device_name=data.get("device_name"),
            device_type=data.get("device_type"),
            count=data.get("count", 1),
            managed_by_user_id=data.get("managed_by_user_id"),
            id=data.get("id"),
            creation_date=data.get("creation_date"),
            last_update=data.get("last_update"),
        )

    def set_managed_by_user_id(self, managed_by_user_id: str):
        self.managed_by_user_id = managed_by_user_id

    def __str__(self) -> str:
        return (
            f"{self.device_type} | {self.device_name} (x{self.count}) "
            f"| Manager: {self.managed_by_user_id}"
        )
