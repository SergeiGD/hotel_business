from sqlalchemy.exc import IntegrityError
from ..models.tags import Tag
from sqlalchemy.orm import Session


class TagsGateway:
    @staticmethod
    def save_tag(tag: Tag, db: Session):
        db.add(tag)
        try:
            db.commit()
        except IntegrityError:
            raise ValueError('тег с таким наименованием уже существует')

    @staticmethod
    def delete_tag(tag: Tag, db: Session):
        db.delete(tag)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Tag).all()

    @staticmethod
    def get_by_id(tag_id: int, db: Session):
        return db.query(Tag).filter_by(id=tag_id).first()
