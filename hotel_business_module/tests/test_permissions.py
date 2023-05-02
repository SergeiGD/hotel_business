from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.users_gateway import UsersGateway
from hotel_business_module.gateways.permissions_gateway import PermissionsGateway
from hotel_business_module.gateways.workers_gateway import WorkersGateway
from hotel_business_module.gateways.groups_gateway import GroupsGateway
from hotel_business_module.models.users import Worker
from hotel_business_module.models.permissions import Permission
from hotel_business_module.models.groups import Group
from hotel_business_module.tests.session import get_session


class TestPermissions(BaseTest):
    def test_can_action(self):
        """
        Тестирование проверки прав доступа
        """
        with get_session() as session:
            # создаем разрешения
            first_permission = Permission(name='first_permission', code='first_permission')
            second_permission = Permission(name='second_permission', code='second_permission')
            PermissionsGateway.save_permission(first_permission, session)
            PermissionsGateway.save_permission(second_permission, session)

            # создаем группу
            group = Group(name='test_group')
            GroupsGateway.save_group(group, session)

            # добавим в группу только одно из двух разрешений
            GroupsGateway.add_permission_to_group(group, first_permission, session)

            # создаем сотрудника
            worker = Worker(email='test@mail.com', salary=50000)
            WorkersGateway.save_worker(worker, session)

            # добавляем сотрудника в группу
            WorkersGateway.add_group_to_worker(worker, group, session)

            # первое разрешение есть, должно вернуть True
            self.assertTrue(UsersGateway.can_actions(
                user=worker,
                codes=[first_permission.code, ],
                db=session
            ))

            # второго разрешения нет, должно вернуть False
            self.assertFalse(UsersGateway.can_actions(
                user=worker,
                codes=[second_permission.code, ],
                db=session
            ))

            # если не хватает хоть одного разрешения, то должно вернуть False
            self.assertFalse(UsersGateway.can_actions(
                user=worker,
                codes=[first_permission.code, second_permission.code, ],
                db=session
            ))

            # дадим статус суперпользователя
            worker.is_superuser = True
            WorkersGateway.save_worker(worker, session)
            # со статусом суперпользователя должно вернуть True, даже если не хватает прав
            self.assertTrue(UsersGateway.can_actions(
                user=worker,
                codes=[first_permission.code, second_permission.code, ],
                db=session
            ))
