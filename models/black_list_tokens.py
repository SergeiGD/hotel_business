from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class BlackListJWT(Base):
    __tablename__ = 'black_list_jwt'
    REPR_MODEL_NAME = 'использованный токен'

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(index=True)
