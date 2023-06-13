from datetime import date, timedelta, datetime
from typing import Optional
import math
from sqlalchemy import func, text, desc
from ..models.categories import Category
from ..models.rooms import Room
from ..models.tags import Tag, category_tag
from ..models.sales import Sale
from ..models.orders import Purchase
from ..settings import settings
from hotel_business_module.utils.file_manager import FileManager
from hotel_business_module.utils.protocols import SupportsReading, SupportsAsyncReading
from sqlalchemy.orm import Session


class CategoriesGateway:
    """
    Класс для управления категориями
    """
    @staticmethod
    def pick_room(
            category: Category,
            start: date,
            end: date,
            db: Session,
            purchase_id: int | None = None
    ) -> int | None:
        """
        Поиск свободной комнаты категории
        :param category: категория, у которой нужно найти комнату
        :param start: дата начала брони
        :param end: дата конца брони
        :param db: сессия БД
        :param purchase_id: id покупки, если нужно подобрать комнату для обновления покупки, а не создания новой
        :return: id комнаты, если нашлась подходящая, иначе None
        """
        # комнаты категории
        rooms = db.query(Room).filter(
            Room.date_deleted == None,
            Room.category_id == category.id,
        ).with_entities(Room.id).all()
        # id комнат категории
        free_rooms = {item[0] for item in rooms}
        # обявления первого дня проверки
        day_to_check = start

        while free_rooms and day_to_check < end:
            # занятые комнаты на проверяемую дату
            busy_rooms = db.query(Purchase).filter(
                Purchase.room_id.in_(free_rooms),
                Purchase.is_canceled == False,
                Purchase.start <= day_to_check,
                Purchase.end > day_to_check,
                Purchase.id != purchase_id
            ).with_entities(Purchase.room_id).all()

            # убираем занятые комнаты
            free_rooms -= {item[0] for item in busy_rooms}
            # передвигаем день
            day_to_check += timedelta(days=1)

        if not free_rooms:
            return None

        # т.к. может вернуться несколько подходящих комнат, возвращаем первую
        picked_room_id = list(free_rooms)[0]
        return picked_room_id

    @staticmethod
    def get_busy_dates(category: Category, date_start: date, date_end: date, db: Session):
        """
        Получение занятых дней комнат категории
        :param category: категория, комнаты которой нужно проверить
        :param date_start: дата начала проверки
        :param date_end: дата конца проверки
        :param db: сессия БД
        :return:
        """
        if date_end < date.today():
            # если запрашиваем прошедшие даты, то проверять смысла нету и возвращаем, что все занято
            return sorted([
                date_start + timedelta(days=x) for x in range((date_end - date_start).days + 1)
            ])

        current_day = date_start
        busy_dates = []
        while current_day <= date_end:
            # проверяем занят ли день и не прошедшая ли дата
            if current_day < date.today() or CategoriesGateway.is_day_busy(category, current_day, db):
                busy_dates.append(current_day)
            current_day += timedelta(days=1)
        # сортируем даты
        busy_dates.sort()
        return busy_dates

    @staticmethod
    def is_day_busy(category: Category, day: date, db: Session):
        """
        Проверка, забронированны ли все комнаты выбранной категории на этот день
        :param category: категория, комнаты которой нужно проверить
        :param day: дата, на которую будет осуществлена проверка
        :param db: сессия БД
        :return:
        """
        #  если нету комнат, то возвращаем как занятно
        if not db.query(
                db.query(Room).filter(
                    Room.category_id == category.id,
                    Room.date_deleted == None,
                ).exists()
        ).scalar():
            return True

        # получаем брони, которые есть на этот день
        purchases = db.query(Purchase.room_id).filter(
            Purchase.start <= day,
            Purchase.end > day,
            Purchase.is_canceled == False
        ).subquery('purchases')

        # если есть хоть одна комната, на которую нету брони в этот день, то есть свободная
        if db.query(
                db.query(Room).filter(
                    Room.category_id == category.id,
                    Room.date_deleted == None,
                    Room.id.not_in(
                        purchases
                    )
                ).exists()
        ).scalar():
            return False
        return True

    @staticmethod
    def get_familiar(category: Category, db: Session):
        """
        Получение похожих категория (с похожими тегами)
        :param category:  категория, для которой нужно найти похожие категории
        :param db: сессия БД
        :return: список похожих категорий
        """
        # Получаем id тегов переданной категории
        tags = db.query(category_tag.c.tag_id).filter(
            category_tag.c.tag_id.in_(
                db.query(category_tag.c.tag_id).filter(
                    category_tag.c.category_id == category.id
                )
            )
        )

        #  Получаем id категорий, у которых есть такие эе теги, как у переданной category
        cats = db.query(category_tag.c.category_id).filter(
            category_tag.c.tag_id.in_(tags),
            category_tag.c.category_id != category.id
        )

        # получаем id 3-х категорий, у которых больше всего совпадений по тегам
        familiar_ids = db.query(
            category_tag.c.category_id.label('cat'),
            func.count(category_tag.c.tag_id).label('count'),
        ).filter(
            category_tag.c.category_id.in_(cats),
            category_tag.c.tag_id.in_(tags),
        ).group_by(text('cat')).order_by(desc('count')).limit(3).all()

        #  получаем сами объекты категорий из полученного кортежа (cat_id, count_tags)
        familiar_items = db.query(Category).filter(
            Category.id.in_([item[0] for item in familiar_ids])
        ).all()
        return familiar_items

    @staticmethod
    def filter(db: Session, filter: dict | None = None):
        """
        Фильтрация категорий
        :param filter: параметры сортировки
        :param db: сессия БД
        :return:
        """
        if filter is None:
            # если не передан фильтр, то ставим стандратные значения у необходимых ключей
            filter = {
                'show_hidden': False,
                'desc': False,
                'page_size': 8,
                'page': 1,
                'sort_by': 'id',
            }
        categories = db.query(Category).filter_by(date_deleted=None)
        if not filter['show_hidden']:
            categories = categories.filter_by(is_hidden=False)
        if 'id' in filter:
            categories = categories.filter(
                Category.id == filter['id']
            )
        if 'name' in filter:
            categories = categories.filter(
                Category.name.icontains(filter['name'])
            )
        if 'beds_from' in filter:
            categories = categories.filter(
                Category.beds >= filter['beds_from']
            )
        if 'beds_until' in filter:
            categories = categories.filter(
                Category.beds <= filter['beds_until']
            )
        if 'floors_from' in filter:
            categories = categories.filter(
                Category.floors >= filter['floors_from']
            )
        if 'floors_until' in filter:
            categories = categories.filter(
                Category.floors <= filter['floors_until']
            )
        if 'square_from' in filter:
            categories = categories.filter(
                Category.square >= filter['square_from']
            )
        if 'square_until' in filter:
            categories = categories.filter(
                Category.square <= filter['square_until']
            )
        if 'price_from' in filter:
            categories = categories.filter(
                Category.price >= filter['price_from']
            )
        if 'price_until' in filter:
            categories = categories.filter(
                Category.price <= filter['price_until']
            )
        if 'rooms_from' in filter:
            categories = categories.filter(
                Category.rooms_count >= filter['rooms_from']
            )
        if 'rooms_until' in filter:
            categories = categories.filter(
                Category.rooms_count <= filter['rooms_until']
            )
        if 'free_dates' in filter:
            categories_to_check = categories.all()
            date_from = filter['free_dates']['date_from']
            date_until = filter['free_dates']['date_until']
            if (date_until - date_from).days > 31:
                raise ValueError('нельзя запросить больше 31 дня')
            busy_categories_ids = []
            for category in categories_to_check:
                if CategoriesGateway.get_busy_dates(category, date_from, date_until, db=db):
                    busy_categories_ids.append(category.id)
            categories = categories.filter(
                Category.id.not_in(busy_categories_ids)
            )

        if filter['desc']:
            categories = categories.order_by(desc(filter['sort_by']))
        else:
            categories = categories.order_by(filter['sort_by'])

        if filter['page_size'] < 1 or filter['page'] < 1:
            raise ValueError('страница и кол-во выводимых элментов не может быть меньше 1')

        limit = filter['page_size']
        offset = filter['page_size'] * (filter['page'] - 1)
        pages_count = math.ceil(categories.count() / filter['page_size'])
        return categories.offset(offset).limit(limit).all(), pages_count

    @staticmethod
    def save_category(
            category: Category,
            db: Session,
            file: SupportsReading | None = None,
            file_name: str | None = None,
    ):
        db.add(category)
        if file is not None and file_name is not None:
            category.main_photo_path = FileManager.save_file(
                file=file, file_name=file_name, old_path=category.main_photo_path
            )
        db.commit()

    @staticmethod
    async def asave_category(
            category: Category,
            db: Session,
            file: SupportsAsyncReading | None = None,
            file_name: str | None = None
    ):
        db.add(category)
        if file is not None and file_name is not None:
            category.main_photo_path = await FileManager.asave_file(
                file=file, file_name=file_name, old_path=category.main_photo_path
            )
        db.commit()

    @staticmethod
    def delete_category(category: Category, db: Session):
        db.add(category)
        category.date_deleted = datetime.now(tz=settings.TIMEZONE)
        FileManager.delete_file(category.main_photo_path)
        for photo in category.photos:
            FileManager.delete_file(photo.path)
        db.commit()

    @staticmethod
    def add_tag_to_category(category: Category, tag: Tag, db: Session):
        db.add(category)
        category.tags.append(tag)
        db.commit()

    @staticmethod
    def remove_tag_from_category(category: Category, tag: Tag, db: Session):
        db.add(category)
        if tag in category.tags:
            category.tags.remove(tag)
        db.commit()

    @staticmethod
    def add_sale_to_category(category: Category, sale: Sale, db: Session):
        db.add(category)
        category.sales.append(sale)
        db.commit()

    @staticmethod
    def remove_sale_to_category(category: Category, sale: Sale, db: Session):
        db.add(category)
        if sale in category.sales:
            category.sales.remove(sale)
        db.commit()

    @staticmethod
    def get_all(db: Session):
        return db.query(Category).filter(Category.date_deleted == None).all()

    @staticmethod
    def get_by_id(category_id: int, db: Session):
        return db.query(Category).filter_by(id=category_id, date_deleted=None).first()
