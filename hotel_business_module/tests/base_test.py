from hotel_business_module.models.base import Base
from hotel_business_module.tests.session import engine
import unittest


class BaseTest(unittest.TestCase):
    """
    Базовый класс для CRUD тестов
    """
    def setUp(self):
        # создаем БД
        Base.metadata.create_all(engine)

    def tearDown(self):
        # удаляем БД
        Base.metadata.drop_all(engine)
