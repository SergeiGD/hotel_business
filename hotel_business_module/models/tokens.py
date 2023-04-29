from datetime import datetime, timedelta
import enum
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy.types import Enum
from ..settings import settings
import hotel_business_module.models.users as users


class TokenType(enum.Enum):
    register = 1
    reset = 2


class Token(Base):
    __tablename__ = 'token'
    REPR_MODEL_NAME = 'токен'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(index=True)
    is_used: Mapped[bool] = mapped_column(default=False)
    token_type: Mapped[TokenType] = mapped_column(Enum(TokenType))
    expires: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=settings.TIMEZONE) + timedelta(days=1),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('people.id'))
    user: Mapped['users.User'] = relationship()
