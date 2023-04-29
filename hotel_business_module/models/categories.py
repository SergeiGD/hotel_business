from typing import Optional, List
from _decimal import Decimal
from datetime import datetime
from ..settings import settings
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import DECIMAL
from .base import Base
import hotel_business_module.models.rooms as rooms
import hotel_business_module.models.tags as tags
import hotel_business_module.models.photos as photos
import hotel_business_module.models.sales as sales


class Category(Base):
    __tablename__ = 'category'
    REPR_MODEL_NAME = 'категория'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2))
    prepayment_percent: Mapped[float]
    refund_percent: Mapped[float]
    main_photo_path: Mapped[str]
    rooms_count: Mapped[int]
    floors: Mapped[int]
    beds: Mapped[int]
    square: Mapped[float]
    date_created: Mapped[datetime] = mapped_column(default=datetime.now(tz=settings.TIMEZONE))
    date_deleted: Mapped[Optional[datetime]] = mapped_column(index=True)
    is_hidden: Mapped[bool] = mapped_column(default=False, index=True)

    tags: Mapped[List['tags.Tag']] = relationship(
        secondary='category_tag',
        back_populates='categories'
    )
    sales: Mapped[List['sales.Sale']] = relationship(
        secondary='category_sale',
        back_populates='categories'
    )

    rooms: Mapped[List['rooms.Room']] = relationship(back_populates='category')
    photos: Mapped[List['photos.Photo']] = relationship(back_populates='category')

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError('Цена должна быть больше 0')
        return price

    @validates('refund_percent')
    def validate_refund_percent(self, key, refund_percent):
        if refund_percent < 0 or refund_percent > 100:
            raise ValueError('Возврат не может быть меньше 0 и больше 100')
        return refund_percent

    @validates('prepayment_percent')
    def validate_prepayment_percent(self, key, prepayment_percent):
        if prepayment_percent < 0 or prepayment_percent > 100:
            raise ValueError('Предоплата не может быть меньше 0 и больше 100')
        return prepayment_percent

    @validates('rooms')
    def validate_rooms(self, key, rooms):
        if rooms <= 0:
            raise ValueError('Кол-во комнат не может быть меньше 1')
        return rooms

    @validates('floors')
    def validate_floors(self, key, floors):
        if floors <= 0:
            raise ValueError('Кол-во этажей не может быть меньше 1')
        return floors

    @validates('beds')
    def validate_beds(self, key, beds):
        if beds <= 0:
            raise ValueError('Кол-во кроватей не может быть меньше 1')
        return beds

    @validates('square')
    def validate_square(self, key, square):
        if square < 20:
            raise ValueError('Площадь не может быть меньше 20')
        return square
