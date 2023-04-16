from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Permission(Base):
    __tablename__ = 'permission'
    REPR_MODEL_NAME = 'разрешение'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    code: Mapped[str] = mapped_column(unique=True, index=True)
