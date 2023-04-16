from datetime import datetime
import bcrypt
from sqlalchemy.orm import Session
from ..models.groups import Group
from ..models.users import Worker
from ..settings import settings


class WorkersGateway:
    @staticmethod
    def save_worker(worker: Worker, db: Session):
        db.add(worker)
        db.commit()

    @staticmethod
    def delete_worker(worker: Worker, db: Session):
        db.add(worker)
        worker.date_deleted = datetime.now(tz=settings.TIMEZONE)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Worker).filter_by(date_deleted=None)

    @staticmethod
    def get_by_id(worker_id: int, db: Session):
        return db.query(Worker).filter_by(id=worker_id, date_deleted=None).first()

    @staticmethod
    def create_superuser(email: str, password: str, db: Session):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        super_user = Worker(
            email=email,
            password=hashed_password.decode('utf8'),
            is_superuser=True,
            salary=0,
            is_confirmed=True,
        )
        db.add(super_user)
        db.commit()

    @staticmethod
    def add_group_to_worker(worker: Worker, group: Group, db: Session):
        db.add(worker)
        worker.groups.append(group)
        db.commit()

    @staticmethod
    def remove_group_from_worker(worker: Worker, group: Group, db: Session):
        db.add(worker)
        if group in worker.groups:
            worker.groups.remove(group)
        db.commit()
