from ..models.tags import Tag
from sqlalchemy.orm import Session


class TagsGateway:
    @staticmethod
    def save_tag(tag: Tag, db: Session):
        db.add(tag)
        db.commit()

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
