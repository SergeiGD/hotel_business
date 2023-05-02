from hotel_business_module.models.base import Base
from hotel_business_module.tests.session import engine
from hotel_business_module.tests.session import get_session
import unittest
from unittest.mock import patch


class BaseTest(unittest.TestCase):
    """
    Базовый класс для CRUD тестов
    """

    def setUp(self):
        # создаем БД
        Base.metadata.create_all(engine)
        # Патчим получение сессий в модулях, чтою они использовали тестовое БД
        self.patchers = [
            patch('hotel_business_module.models.rooms.get_session', side_effect=get_session),
            patch('hotel_business_module.models.orders.get_session', side_effect=get_session),
            patch('hotel_business_module.models.users.get_session', side_effect=get_session),
            patch('hotel_business_module.models.photos.get_session', side_effect=get_session),
            patch('hotel_business_module.gateways.photos_gateway.get_session', side_effect=get_session)
        ]
        for item in self.patchers:
            item.start()
        # добавляем остановку патчеров при завершении
        self.addCleanup(self.stop_patches)

    def tearDown(self):
        # закрываем сессию
        # удаляем БД
        Base.metadata.drop_all(engine)

    def stop_patches(self):
        for patcher in self.patchers:
            patcher.stop()
