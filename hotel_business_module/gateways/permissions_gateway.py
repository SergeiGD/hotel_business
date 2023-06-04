from sqlalchemy.exc import IntegrityError

from ..models.permissions import Permission
from sqlalchemy.orm import Session


class PermissionsGateway:
    @staticmethod
    def save_permission(permission: Permission, db: Session):
        db.add(permission)
        try:
            db.commit()
        except IntegrityError:
            raise ValueError('разрешение с таким наименованием уже существует')

    @staticmethod
    def delete_permission(permission: Permission, db: Session):
        db.delete(permission)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Permission).all()

    @staticmethod
    def get_by_id(permission_id: int, db: Session):
        return db.query(Permission).filter_by(id=permission_id).first()
