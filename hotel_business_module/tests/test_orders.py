from typing import Tuple
from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.orders_gateway import OrdersGateway
from hotel_business_module.gateways.clients_gateway import ClientsGateway
from hotel_business_module.gateways.purchase_gateway import PurchasesGateway
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.gateways.rooms_gateway import RoomsGateway
from hotel_business_module.models.rooms import Room
from hotel_business_module.models.categories import Category
from hotel_business_module.models.orders import Order, Purchase
from hotel_business_module.models.users import Client
from hotel_business_module.tests.session import get_session
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from _decimal import Decimal


class TestOrders(BaseTest):
    """
    Тестирование заказов и покупок
    """

    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def spawn_preparation_data(self, session, mock_save_file: Mock) -> Tuple[Category, Room, Client]:
        """
        Метод для создания подготовительных данных
        """
        # мокаем метод сохранения файла, чтоб реально не сохранять, а просто получить имя
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        # мокаем файл, чтоб отправить его как параметр
        file = Mock()
        category = Category(
            name='test_category',
            description='lorem ipsum...',
            price=1000,
            prepayment_percent=20,
            refund_percent=50,
            rooms_count=2,
            floors=1,
            beds=2,
            square=50
        )
        CategoriesGateway.save_category(category, session, file=file, file_name=file.name)

        room = Room(category=category)
        RoomsGateway.save_room(room, session)

        client = Client(email='test@gmail.com', is_confirmed=True)
        ClientsGateway.save_client(client, session)

        return category, room, client

    def test_save(self):
        """
        Тестирование сохранения
        """
        with get_session() as session:
            # создаем необходимые данные
            category, room, client = self.spawn_preparation_data(session)

            order = Order(client=client)
            OrdersGateway.save_order(order, session)

            # проверяем сохранился ли
            self.assertIsNotNone(OrdersGateway.get_by_id(order.id, session))

            purchase = Purchase(order=order, start=datetime(2023, 5, 10), end=datetime(2023, 5, 15))
            PurchasesGateway.save_purchase(purchase=purchase, db=session, category=category)

            self.assertIsNotNone(PurchasesGateway.get_by_id(purchase.id, session))

    def test_price(self):
        """
        Тестирование расчеты цены заказа и покупок
        """
        with get_session() as session:
            # создаем необходимые данные
            category, room, client = self.spawn_preparation_data(session)
            order = Order(client=client)
            OrdersGateway.save_order(order, session)

            # создаем даты начала и конца заказа
            start = datetime(2023, 5, 10)
            end = datetime(2023, 5, 15)
            purchase = Purchase(order=order, start=start, end=end)
            # сохраняем покупки
            PurchasesGateway.save_purchase(purchase=purchase, db=session, category=category)

            # проверяем цену
            price = (end - start).days * purchase.room.category.price
            self.assertEqual(purchase.price, price)
            self.assertEqual(purchase.order.price, price)

            # проверяем предоплату
            prepayment_ratio = Decimal(purchase.room.category.prepayment_percent / 100)
            prepayment = price * prepayment_ratio
            self.assertEqual(purchase.prepayment, prepayment)
            self.assertEqual(purchase.order.prepayment, round(prepayment, 2))

            # проверяем возврат
            refund_ratio = Decimal(purchase.room.category.refund_percent / 100)
            refund = price * refund_ratio
            self.assertEqual(purchase.refund, refund)

            # увеличим кол-во дней брони
            purchase.end = purchase.end + timedelta(days=2)
            PurchasesGateway.save_purchase(purchase, session)
            # проверим, что цена корреткно увеличилась
            new_price = (purchase.end - purchase.start).days * purchase.room.category.price
            self.assertEqual(purchase.price, new_price)
            self.assertEqual(purchase.order.price, new_price)

            # отмечаем заказ как оплаченный
            OrdersGateway.mark_as_paid(order, session)
            # проверяем, что все оплатилось
            self.assertEqual(order.left_to_pay, 0)

            # отменяем заказ
            OrdersGateway.mark_as_canceled(order, session)
            # проверяем, что правильно перерасчиталась цена
            self.assertEqual(order.price, purchase.price - purchase.refund)
            # проверяем, что правильно расчитвает сумму к возврату
            left_to_refund = order.paid - order.price - order.refunded
            self.assertEqual(order.left_to_refund, left_to_refund)

    def test_auth_room_picking(self):
        """
        Тестирование автоматического подбора комнат для покупок
        """
        with get_session() as session:
            # создаем необходимые данные
            category, first_room, client = self.spawn_preparation_data(session)
            order = Order(client=client)
            OrdersGateway.save_order(order, session)

            # создаем еще одну комнату
            second_room = Room(category=category)
            RoomsGateway.save_room(second_room, session)

            # создаем покупки
            first_purchase = Purchase(order=order, start=datetime(2023, 5, 10), end=datetime(2023, 5, 15))
            second_purchase = Purchase(order=order, start=datetime(2023, 5, 12), end=datetime(2023, 5, 17))
            third_purchase = Purchase(order=order, start=datetime(2023, 5, 15), end=datetime(2023, 5, 17))
            fourth_purchase = Purchase(order=order, start=datetime(2023, 5, 11), end=datetime(2023, 5, 20))
            PurchasesGateway.save_purchase(purchase=first_purchase, db=session, category=category)
            PurchasesGateway.save_purchase(purchase=second_purchase, db=session, category=category)
            PurchasesGateway.save_purchase(purchase=third_purchase, db=session, category=category)

            # первой покупке должна присвоится первая комната
            self.assertEqual(first_purchase.room, first_room)
            # второй покупке должна присвоится вторая комната, т.к. первая будет уже занята
            self.assertEqual(second_purchase.room, second_room)
            # третьей покупке должна присвоится третья комната, т.к. в этот день освободится комната
            self.assertEqual(third_purchase.room, first_room)
            # четвертая покупка не должна сохранится, т.к. в это время все комнаты заняты
            self.assertRaises(ValueError, PurchasesGateway.save_purchase, fourth_purchase, session, category)
