from _decimal import Decimal
from datetime import datetime
from sqlalchemy import or_
from ..models.orders import Purchase, Order
from ..settings import settings
from sqlalchemy.orm import Session


class OrdersGateway:
    """
    Класс для управления заказами
    """
    @staticmethod
    def __update_payment(order: Order, db: Session):
        """
        Обновление статуса оплаты
        :param order: заказ, который необходимо обновить
        :return:
        """
        if isinstance(order.paid, float):
            # если обновляли и установили paid, то преводим к decimal
            paid = Decimal(order.paid)
            order.paid = round(paid, 2)

        if order.paid >= order.price and order.paid > 0:
            # если полностью оплачен
            db.query(Purchase).filter(
                Purchase.order_id == order.id,
                Purchase.is_canceled == False,
                Purchase.is_paid == False,
            ).update({'is_paid': True})
            if order.date_full_paid is None:
                order.date_full_paid = datetime.now(tz=settings.TIMEZONE)
            return

        if order.paid >= order.prepayment and order.paid > 0:
            # если оплачена предоплата
            db.query(Purchase).filter(
                Purchase.order_id == order.id,
                Purchase.is_canceled == False,
                Purchase.is_prepayment_paid == False,
            ).update({'is_prepayment_paid': True})
            if order.date_full_prepayment is None:
                order.date_full_prepayment = datetime.now(tz=settings.TIMEZONE)
            return

        if order.paid < order.prepayment:
            # если не оплачено вообще
            db.query(Purchase).filter(
                Purchase.order_id == order.id,
                Purchase.is_canceled == False,
                Purchase.is_prepayment_paid == True,
            ).update({'is_prepayment_paid': False, 'is_paid': False})
            order.date_full_prepayment = None
            order.date_full_paid = None
            return

        if order.paid < order.price:
            # если не оплачена предоплата
            db.query(Purchase).filter(
                Purchase.order_id == order.id,
                Purchase.is_canceled == False,
                Purchase.is_paid == True,
            ).update({'is_paid': False})
            order.date_full_paid = None
            return

    @classmethod
    def save_order(cls, order: Order, db: Session):
        db.add(order)
        if order.id is not None:
            cls.__update_payment(order, db)
        db.commit()

    @staticmethod
    def mark_as_canceled(order: Order, db: Session):
        """
        Отметить заказ как отмененный
        :param order: заказ, который нужно отменить
        :param db: сессия БД
        :return:
        """
        if order.date_canceled is not None:
            return
        db.add(order)
        # устанавливаем дату отмены
        order.date_canceled = datetime.now(tz=settings.TIMEZONE)
        order.date_finished = None
        # отменяем оплаченные покупки
        db.query(Purchase).filter(
            Purchase.order_id == order.id,
            Purchase.is_canceled == False,
            or_(Purchase.is_paid == True, Purchase.is_prepayment_paid == True),
        ).update({'is_canceled': True})
        # удаляем не оплаченные покупки
        db.query(Purchase).filter(
            Purchase.order_id == order.id,
            Purchase.is_canceled == False,
            Purchase.is_paid == False,
            Purchase.is_prepayment_paid == False,
        ).delete()
        db.commit()

    @staticmethod
    def mark_as_paid(order: Order, db: Session):
        if order.date_finished is not None or order.date_canceled is not None:
            raise ValueError('Нельзя оплатить неактивный заказ')
        if order.date_full_paid is not None:
            return
        order.paid = order.price
        OrdersGateway.save_order(order, db)

    @staticmethod
    def finish_orders(db: Session):
        db.query(Purchase).filter(
            Purchase.end < datetime.now(settings.TIMEZONE),
            Purchase.is_paid == False,
            Purchase.is_prepayment_paid == True,
        ).update({'is_canceled': True})

        db.query(Purchase).filter(
            Purchase.end < datetime.now(settings.TIMEZONE),
            Purchase.is_paid == False,
            Purchase.is_prepayment_paid == False,
        ).delete()

        db.query(Order).filter(
            Order.id.not_in(
                db.query(Purchase.order_id).filter(
                    Purchase.end > datetime.now(settings.TIMEZONE),
                )
            ),
            Order.price > 0
        ).update({'date_finished': datetime.now(tz=settings.TIMEZONE)})

        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Order).all()

    @staticmethod
    def get_by_id(order_id: int, db: Session):
        return db.query(Order).filter_by(id=order_id).first()
