from typing import List
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column
import hotel_business_module.models.users as users
import hotel_business_module.models.permissions as permission


group_permission = Table(
    'group_permission',
    Base.metadata,
    Column('group_id', ForeignKey('group.id'), primary_key=True),
    Column('permission_id', ForeignKey('permission.id'), primary_key=True),
)


class Group(Base):
    __tablename__ = 'group'
    REPR_MODEL_NAME = 'группа'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    permissions: Mapped[List['permission.Permission']] = relationship(
        secondary=group_permission,
    )

    users: Mapped[List['users.User']] = relationship(
        secondary='user_group',
        back_populates='groups',
    )
