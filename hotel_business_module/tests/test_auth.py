from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.clients_gateway import ClientsGateway
from hotel_business_module.gateways.users_gateway import UsersGateway
from hotel_business_module.models.tokens import TokenType
from hotel_business_module.models.users import Client
from hotel_business_module.tests.session import get_session


class TestTags(BaseTest):
    def test_login(self):
        """
        Тестирование аутентификации
        """
        with get_session() as session:
            email = 'test@gmail.ru'
            password = 'passwd123'
            # регистрируем пользователя
            client, token = UsersGateway.register_user(Client(email=email, password=password), session)
            # проверяем и получаем объект токен
            token_obj = UsersGateway.check_token(token, TokenType.register, session)
            # подтверждаем аккаунт
            UsersGateway.confirm_account(token_obj, session)
            # пробуем войти с правильными данными
            self.assertEqual(client, UsersGateway.authenticate_user(email, password, session))
            # пробуем войти с неправильными данными
            self.assertRaises(ValueError, UsersGateway.authenticate_user, email, 'wrong_passwrd', session)
            self.assertRaises(ValueError, UsersGateway.authenticate_user, 'wrong_login', password, session)

    def test_register(self):
        """
        Тестирование регистрации
        """
        with get_session() as session:
            email = 'test@gmail.ru'
            password = 'passwd123'
            # регистрируем пользователя
            client, token = UsersGateway.register_user(Client(email=email, password=password), session)
            # проверяем, что пользователь создался
            self.assertIsNotNone(UsersGateway.get_by_id(client.id, session))
            # проверяем, что аккаунт не подтвержден
            self.assertFalse(client.is_confirmed)
            # проверяем и получаем объект токен
            token_obj = UsersGateway.check_token(token, TokenType.register, session)
            # подтверждаем токен
            UsersGateway.confirm_account(token_obj, session)
            # проверяем, что аккаунт подтвердился
            self.assertTrue(client.is_confirmed)
            # проверяем, что не можем зарегистрировать пользователя с такой же почтой
            self.assertRaises(ValueError, UsersGateway.register_user, client, session)

    def test_reset(self):
        """
        Тестирование сброса пароля
        """
        with get_session() as session:
            email = 'test@gmail.ru'
            password = 'passwd123'
            # регистрируем пользователя
            client, token = UsersGateway.register_user(Client(email=email, password=password), session)
            # проверяем и получаем объект токен
            token_obj = UsersGateway.check_token(token, TokenType.register, session)
            # подтверждаем аккаунт
            UsersGateway.confirm_account(token_obj, session)
            _, token = UsersGateway.request_reset(email, session)
            # проверяем и получаем объект токена
            token_obj = UsersGateway.check_token(token, TokenType.reset, session)
            new_password = 'new_password'
            # сохраняем с новым паролем
            UsersGateway.confirm_reset(token_obj, new_password, session)
            # пробуем войти по новому паролю
            self.assertEqual(client, UsersGateway.authenticate_user(email, new_password, session))
            # пробуем войти по старому паролю
            self.assertRaises(ValueError, UsersGateway.authenticate_user, email, password, session)
