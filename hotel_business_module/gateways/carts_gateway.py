from ..models.orders import Purchase, Order, Cart
from ..models.users import User, Client
from .clients_gateway import ClientsGateway
from .orders_gateway import OrdersGateway
from ..settings import settings
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


class CartsGateway:
    @staticmethod
    def confirm_cart(cart: Cart, email: str, db: Session, is_fully_paid: bool = False):
        client = db.query(User).filter(
            User.email == email,
        ).first()
        if client is None:
            client = Client(email=email)
            ClientsGateway.save_client(client, db)

        order = Order(client=client)
        OrdersGateway.save_order(order, db)
        db.query(Purchase).filter(
            Purchase.order_id == cart.id,
        ).update({'order_id': order.id})
        db.refresh(cart)
        db.delete(cart)
        db.commit()

        if is_fully_paid:
            order.paid = cart.price
        else:
            order.paid = cart.prepayment
        OrdersGateway.save_order(order, db)

        return order

    @staticmethod
    def clean_carts(db: Session):
        db.query(Cart).filter(
            Cart.date_created < datetime.now(tz=settings.TIMEZONE) - timedelta(hours=24)
        ).delete()
        db.commit()

    @staticmethod
    def save_cart(cart: Cart, db: Session):
        db.add(cart)
        db.commit()

    @staticmethod
    def get_by_uuid(cart_uuid: str, db: Session):
        return db.query(Cart).filter_by(cart_uuid=cart_uuid).first()
