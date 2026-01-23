from serializable import Serializable
from database import DatabaseConnector
from datetime import datetime
from typing import Self

class Reservation(Serializable):

    db_connector =  DatabaseConnector().get_table("reservations")

    def __init__(self, user_id: str, device_id: str, start_date: datetime, end_date: datetime, purpose: str = "", costs: float = None, creation_date: datetime = None, last_update: datetime = None, id: str = None) -> None:

        if not id:
            id = F"{user_id}_{device_id}_{start_date}"

        super().__init__(id, creation_date, last_update)
        self.user_id = user_id
        self.device_id = device_id
        self.start_date = start_date
        self.end_date = end_date
        self.purpose = purpose
        self.costs = costs
        
    @classmethod
    def instantiate_from_dict(cls, data: dict) -> Self:

        def to_dt(x):
            if isinstance(x, str):
                return datetime.fromisoformat(x)
            return x

        return cls(
            data["user_id"],
            data["device_id"],
            to_dt(data["start_date"]),
            to_dt(data["end_date"]),
            data.get("purpose", ""),
            data.get("costs"),
            to_dt(data.get("creation_date")),
            to_dt(data.get("last_update")),
            data["id"]
        )

    def __str__(self):
        return f"Reservation: {self.user_id} für {self.device_id} ({self.purpose}): {self.start_date} - {self.end_date}"

