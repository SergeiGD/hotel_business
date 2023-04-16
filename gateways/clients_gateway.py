from datetime import datetime
from sqlalchemy.orm import Session
from ..models.users import Client
from ..settings import settings
from ..models.orders import Order


class ClientsGateway:
    """
    Класс для управления клиентами
    """
    @staticmethod
    def save_client(client: Client, db: Session):
        db.add(client)
        db.commit()

    @staticmethod
    def delete_client(client: Client, db: Session):
        db.add(client)
        client.date_deleted = datetime.now(tz=settings.TIMEZONE)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Client).filter_by(date_deleted=None)

    @staticmethod
    def get_by_id(client_id: int, db: Session):
        return db.query(Client).filter_by(id=client_id, date_deleted=None).first()

    @staticmethod
    def get_all_client_orders(clint: Client, db: Session):
        return db.query(Order).filter_by(client_id=clint.id)

    @staticmethod
    def get_client_order_by_id(clint: Client, order_id: int, db: Session):
        return db.query(Order).filter_by(id=order_id, client_id=clint.id).first()
