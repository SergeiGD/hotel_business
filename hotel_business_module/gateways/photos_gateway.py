from typing import Optional
from sqlalchemy import inspect, func
from ..models.photos import Photo
from hotel_business_module.utils.file_manager import FileManager
from ..session.session import get_session
from sqlalchemy.orm import Session
from hotel_business_module.utils.protocols import SupportsReading, SupportsAsyncReading


class PhotosGateway:
    """
    Класс для управления фотографиями
    """
    @staticmethod
    def __swap_photos(photo: Photo):
        """
        Метод для перестановки фотографий местами
        :param photo: фото, которому обновляем порядок
        :return:
        """
        # создаем отдельную сессию, чтоб получить изначальный порядковый номер фотографии
        with get_session() as db:
            category_id = photo.category_id if photo.category_id is not None else photo.category.id
            # ищем фотографию, с которой поменяется местами
            photo_to_swap = db.query(Photo).filter(
                Photo.category_id == category_id,
                Photo.order == photo.order
            ).first()
            if photo_to_swap is None:
                raise ValueError('Не найдена фотография с таким номером')

            # меняем местами фотографии
            current_order = db.get(Photo, photo.id).order
            photo_to_swap.order = current_order
            # db.expunge(photo)
            db.add(photo_to_swap)
            db.commit()

    @staticmethod
    def delete_photo(photo: Photo, db: Session):
        """
        Удалить фотографию
        :param photo: фотографию, которую нужно удалить
        :param db: сессия
        :return:
        """
        db.refresh(photo)
        category_id = photo.category_id if photo.category_id is not None else photo.category.id

        # все последующий фотографии сдвигаем на 1
        db.query(Photo).filter(
            Photo.category_id == category_id,
            Photo.order > photo.order,
        ).update({'order': Photo.order - 1})
        # удаляем фото
        FileManager.delete_file(photo.path)
        db.delete(photo)
        db.commit()

    @classmethod
    def __presave_action(
            cls,
            photo: Photo,
            db: Session,
    ):
        # если обновляли и поменяли порядок, то меняем местами
        if photo.order is not None and inspect(photo).attrs.order.history.has_changes():
            cls.__swap_photos(photo)

        db.add(photo)
        # если создали новую, то автоматическа установливаем порядок (ставим последней)
        if photo.id is None and photo.order is None:
            category_id = photo.category_id if photo.category_id is not None else photo.category.id
            #  ищем текущую крайнюю фотографию категории
            current_max = db.query(func.max(Photo.order)).filter(
                Photo.category_id == category_id
            ).scalar()
            if current_max is None:
                # если это первая фотография категории, то ставим 1
                photo.order = 1
            else:
                photo.order = current_max + 1

    @classmethod
    def save_photo(
            cls,
            photo: Photo,
            db: Session,
            file: SupportsReading | None = None,
            file_name: str | None = None,
    ):
        cls.__presave_action(photo, db)

        if file is not None and file_name is not None:
            path = FileManager.save_file(file=file, file_name=file_name, old_path=photo.path)
            photo.path = path

        db.commit()

    @classmethod
    async def asave_photo(
            cls,
            photo: Photo,
            db: Session,
            file: SupportsAsyncReading | None = None,
            file_name: str | None = None,
    ):
        cls.__presave_action(photo, db)

        if file is not None and file_name is not None:
            photo.path = await FileManager.asave_file(
                file=file, file_name=file_name, old_path=photo.path
            )

        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Photo).all()

    @staticmethod
    def get_by_id(photo_id: int, db: Session):
        return db.query(Photo).filter_by(id=photo_id).first()
