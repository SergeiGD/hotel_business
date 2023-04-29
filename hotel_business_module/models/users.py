from datetime import datetime, date
from _decimal import Decimal
from typing import List
from ..settings import settings
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import ForeignKey, Table, Column, event
from typing import Optional
from .base import Base
import hotel_business_module.models.orders as orders
import hotel_business_module.models.groups as groups
from ..session.session import get_session


user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', ForeignKey('people.id'), primary_key=True),
    Column('group_id', ForeignKey('group.id'), primary_key=True),
)


class User(Base):
    __tablename__ = 'people'
    REPR_MODEL_NAME = 'пользователь'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    email: Mapped[str]
    password: Mapped[Optional[str]]
    date_created: Mapped[datetime] = mapped_column(default=datetime.now(tz=settings.TIMEZONE))
    date_deleted: Mapped[Optional[datetime]]
    is_confirmed: Mapped[bool] = mapped_column(default=False)
    type: Mapped[str]

    orders: Mapped[List['orders.Order']] = relationship(back_populates='client', viewonly=True)

    groups: Mapped[List['groups.Group']] = relationship(
        secondary=user_group,
        back_populates='users',
    )

    __mapper_args__ = {
        'polymorphic_abstract': True,
        'polymorphic_on': 'type',
    }

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Неверный формат адреса эл. почты')

        return email


class Client(User):
    __tablename__ = 'client'
    REPR_MODEL_NAME = 'клиент'

    id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    date_of_birth: Mapped[Optional[date]]
    orders: Mapped[List['orders.Order']] = relationship(back_populates='client')

    __mapper_args__ = {
        'polymorphic_identity': 'client',
    }


class Worker(User):
    __tablename__ = 'worker'
    REPR_MODEL_NAME = 'сотрудник'

    id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    salary: Mapped[Decimal]

    __mapper_args__ = {
        'polymorphic_identity': 'worker',
    }


def validate_unq_email(mapper, connection, target: User):
    with get_session() as db:
        if db.query(
                db.query(User).filter(
                    User.email == target.email,
                    User.date_deleted == None,
                ).exists()
        ).scalar():
            raise ValueError('Уже есть пользователь с таким адреос эл. почты')


event.listen(Client, 'before_insert', validate_unq_email)
event.listen(Worker, 'before_insert', validate_unq_email)
