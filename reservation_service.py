from datetime import datetime
from reservations import Reservation
from devices_inheritance import Device
from users_inheritance import User


class ReservationService():

    def __init__(self) -> None:
        self.find_all_reservations()

    @classmethod
    def find_all_reservations(cls) -> list[Reservation]:
        cls.reservations = Reservation.find_all()
        return cls.reservations

    @classmethod
    def find_all_reservations_by_user_id(cls, user_id: str) -> list[Reservation]:
        return [reservation for reservation in cls.reservations if reservation.user_id == user_id]
    
    @classmethod
    def find_all_reservations_by_device_id(cls, device_id: str) -> list[Reservation]:
        return [reservation for reservation in cls.reservations if reservation.device_id == device_id]    
    
    @classmethod
    def find_all_reservations_by_user_id_and_device_id(cls, user_id: str, device_id: str) -> list[Reservation]:
        return [reservation for reservation in cls.reservations if reservation.device_id == device_id and reservation.user_id == user_id]

    @classmethod
    def check_conflict(cls, device_id: str, start_date: datetime, end_date: datetime) -> bool:
        for reservation in cls.reservations:
            if reservation.device_id == device_id:
                if (start_date >= reservation.start_date and start_date <= reservation.end_date) or (end_date >= reservation.start_date and end_date <= reservation.end_date):
                    return True
        return False

    @staticmethod
    def user_exists(user_id: str) -> bool:
        return User.find_by_attribute("id", user_id) is not None

    @staticmethod
    def device_exists(device_id: str) -> bool:
        return Device.find_by_attribute("id", device_id) is not None
    
    @classmethod
    def create_reservation(cls, user_id: str, device_id: str, start_date: str | datetime, end_date: str | datetime, purpose: str = "", costs: float = None) -> bool:
        if not cls.user_exists(user_id):
            raise ValueError("User does not exist")
        
        if not cls.device_exists(device_id):
            raise ValueError("Device does not exist")
        
        # If the dates are provided as strings, convert them to datetime objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

        if cls.check_conflict(device_id, start_date, end_date):
            raise ValueError("Reservation conflict detected")
        
        reservation = Reservation(user_id, device_id, start_date, end_date, purpose=purpose, costs=costs)
        reservation.store_data()
        cls.find_all_reservations()
        return True


if __name__ == "__main__":
    # Create a device
    reservation_service = ReservationService()

