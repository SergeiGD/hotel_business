from ..models.permissions import Permission
from sqlalchemy.orm import Session


class PermissionsGateway:
    @staticmethod
    def get_all(db: Session):
        return db.query(Permission).all()

    @staticmethod
    def get_by_id(permission_id: int, db: Session):
        return db.query(Permission).filter_by(id=permission_id).first()
