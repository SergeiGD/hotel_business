from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.clients_gateway import ClientsGateway
from hotel_business_module.models.users import Client
from hotel_business_module.tests.session import get_session


class TestTags(BaseTest):
    def test_save(self):
        """
        Тестирование сохранения клиентов
        """
        with get_session() as session:
            client = Client(email='test@gmail.ru')
            # сохраняем клиента
            ClientsGateway.save_client(client, session)

            # проверяем сохранился ли
            self.assertIsNotNone(ClientsGateway.get_by_id(client.id, session))

            # создаем клиента с таким же адресом эл. почты
            dup_client = Client(email=client.email)

            # проверяем, чтоб вернул ошибку при создании клиента с таким же адресом эл. почты
            self.assertRaises(ValueError, ClientsGateway.save_client, dup_client, session)
            # проверяем, что не сохранил
            self.assertIsNone(dup_client.id)

    def test_delete(self):
        """
        Тестирование удаление клиента
        """
        with get_session() as session:
            client = Client(email='test@gmail.ru')
            # сохраняем клиента
            ClientsGateway.save_client(client, session)

            # удаляем клинте
            ClientsGateway.delete_client(client, session)
            # проверяем, что удалился
            self.assertIsNone(ClientsGateway.get_by_id(client.id, session))

            # создаем клиента с почтой удаленного
            dup_client = Client(email=client.email)

            # проверяем, что сохранился -> почта освободилась
            ClientsGateway.save_client(dup_client, session)
            self.assertIsNotNone(ClientsGateway.get_by_id(dup_client.id, session))
