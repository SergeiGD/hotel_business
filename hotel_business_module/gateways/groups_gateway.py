from ..models.groups import Group
from ..models.permissions import Permission
from sqlalchemy.orm import Session


class GroupsGateway:
    @staticmethod
    def save_group(group: Group, db: Session):
        db.add(group)
        db.commit()

    @staticmethod
    def delete_group(group: Group, db: Session):
        db.delete(group)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Group).all()

    @staticmethod
    def get_by_id(group_id: int, db: Session):
        return db.query(Group).filter_by(id=group_id).first()

    @staticmethod
    def add_permission_to_group(group: Group, permission: Permission, db: Session):
        db.add(group)
        group.permissions.append(permission)
        db.commit()

    @staticmethod
    def remove_permission_from_group(group: Group, permission: Permission, db: Session):
        db.add(group)
        group.permissions.remove(permission)
        db.commit()
        