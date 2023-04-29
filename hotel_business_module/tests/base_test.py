from hotel_business_module.models.base import Base
from hotel_business_module.tests.session import engine
import unittest


class BaseTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)

    def tearDown(self):
        Base.metadata.drop_all(engine)
