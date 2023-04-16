from _decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from ..models.orders import Purchase
from ..models.categories import Category
from ..models.sales import Sale
from ..models.rooms import Room
from .categories_gateway import CategoriesGateway
from .orders_gateway import OrdersGateway
from ..models.orders import Order
from sqlalchemy.orm import Session


class PurchasesGateway:
    """
    Класс для управления покупками заказа
    """
    @staticmethod
    def __set_price(purchase: Purchase, db: Session):
        """
        Установка цен покупки
        :param purchase: покупка, которой нужно установить цены
        :return:
        """
        # берем категории комнаты, на которую оформлена покупка
        category: Category = db.query(Room).get(purchase.room_id).category
        # считаем продолжительность покупки
        delta_seconds: Decimal = (purchase.end - purchase.start).total_seconds()
        SECONDS_IN_DAY: int = 86400
        # считаем на сколько дней покупка
        days: int = round(Decimal(delta_seconds / SECONDS_IN_DAY), 0)
        # стандартная цена
        default_price: Decimal = category.price * days
        # ищем, есть ли активные скидки и если есть, то берем максимальную
        sale = db.query(func.max(Sale.discount)).filter(
            Sale.start_date <= datetime.now(),
            Sale.end_date >= datetime.now(),
            Sale.date_deleted == None,
            Sale.categories.any(id=category.id)
        ).scalar()
        if sale:
            # если есть скидка, то считаем цену с ее учетом
            sale_ration = Decimal(sale / 100)
            purchase.price = default_price - (default_price * sale_ration)
        else:
            purchase.price = default_price

        # считаем устанавливаем предоплату
        prepayment_ratio = Decimal(category.prepayment_percent / 100)
        purchase.prepayment = purchase.price * prepayment_ratio
        # считаем устанавливаем возврат
        refund_ratio = Decimal(category.refund_percent / 100)
        purchase.refund = purchase.price * refund_ratio

    @staticmethod
    def __set_room(purchase: Purchase, category: Category, db: Session):
        """
        Установка комнаты покупки
        :param purchase: покупка, для которой нужно найти комнату
        :param category: категория, на которую необходимо сделать бронь
        :return:
        """
        # ищем свободную комнату выбранной категории на выбранные даты
        room_id = CategoriesGateway.pick_room(
            category=category,
            start=purchase.start,
            end=purchase.end,
            purchase_id=purchase.id,
            db=db,
        )
        if room_id is None:
            raise ValueError('На эти даты нет свободных комнат этой категории')

        purchase.room_id = room_id

    @classmethod
    def save_purchase(cls, purchase: Purchase, db: Session, category: Optional[Category] = None):
        db.add(purchase)
        category = category if category is not None else purchase.room.category
        cls.__set_room(purchase, category, db)
        cls.__set_price(purchase, db)
        db.commit()

        if isinstance(purchase.order, Order):
            OrdersGateway.save_order(purchase.order, db)

    @staticmethod
    def mark_as_canceled(purchase: Purchase, db: Session):
        db.add(purchase)
        if purchase.is_prepayment_paid or purchase.is_paid:
            purchase.is_canceled = True
        else:
            db.delete(purchase)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Purchase).all()

    @staticmethod
    def get_by_id(purchase_id: int, db: Session):
        return db.query(Purchase).filter_by(id=purchase_id).first()
