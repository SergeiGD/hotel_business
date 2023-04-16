from datetime import datetime
from ..settings import settings
from ..models.rooms import Room
from sqlalchemy import func
from sqlalchemy.orm import Session


class RoomsGateway:
    @staticmethod
    def save_room(room: Room, db: Session):
        db.add(room)

        if room.id is None and room.room_number is None:
            current_max = db.query(func.max(Room.room_number)).filter(
                Room.date_deleted == None
            ).scalar()
            if current_max is None:
                room.room_number = 1
            else:
                room.room_number = current_max + 1

        db.commit()
        # db.refresh(room)

    @staticmethod
    def delete_room(room: Room, db: Session):
        db.add(room)
        room.date_deleted = datetime.now(tz=settings.TIMEZONE)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Room).filter_by(date_deleted=None)

    @staticmethod
    def get_by_id(room_id: int, db: Session):
        return db.query(Room).filter_by(id=room_id, date_deleted=None).first()
