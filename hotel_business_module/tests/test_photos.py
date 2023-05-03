from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.gateways.photos_gateway import PhotosGateway
from hotel_business_module.gateways.photos_gateway import Photo
from hotel_business_module.models.photos import Photo
from hotel_business_module.models.categories import Category
from hotel_business_module.tests.session import get_session


class TestCategories(BaseTest):

    @patch('hotel_business_module.utils.file_manager.FileManager.save_file')
    def test_set_order(self, mock_save_file: Mock):
        """
        Тестирования присвоения порядкового номера категоии
        """
        # мокаем метод сохранения файла, чтоб реально не сохранять, а просто получить имя
        mock_save_file.return_value = 'C:\\images\\image1.jpg'
        # мокаем файл, чтоб отправить его как параметр
        file = Mock()
        with get_session() as session:
            # создаем категории
            category = Category(
                name='test_category',
                description='lorem ipsum...',
                price=999,
                prepayment_percent=10,
                refund_percent=50,
                rooms_count=2,
                floors=1,
                beds=2,
                square=50
            )
            CategoriesGateway.save_category(category, session, file=file, file_name=file.name)

            # создаем первое фото
            first_photo = Photo(category=category)
            PhotosGateway.save_photo(first_photo, session, file=file, file_name=file.name)
            self.assertEqual(first_photo.path, 'C:\\images\\image1.jpg')
            # должен присвоится порядоковый номер 1
            self.assertEqual(first_photo.order, 1)

            # создаем второе фото
            second_photo = Photo(category=category)
            PhotosGateway.save_photo(second_photo, session, file=file, file_name=file.name)
            self.assertEqual(second_photo.path, 'C:\\images\\image1.jpg')
            # должен присвоится порядоковый номер 2
            self.assertEqual(second_photo.order, 2)

            # ставим второй фотографии порядковый номер 2
            second_photo.order = 1
            PhotosGateway.save_photo(second_photo, session, file=file, file_name=file.name)
            self.assertEqual(second_photo.order, 1)
            # у второй должен сменится на 1
            session.refresh(first_photo)
            self.assertEqual(first_photo.order, 2)

            # ставим второй фотографии несуществующий порядковый номер
            second_photo.order = 5
            # должно вернуть ошибку, т.к. не с чем менять местами и сломается порядок
            self.assertRaises(ValueError, PhotosGateway.save_photo, second_photo, session)

            # удаляем второе фото
            PhotosGateway.delete_photo(second_photo, session)
            # у первого порядковый номер должен передвинуться на 1, так как фото с номер 1 удалили
            self.assertEqual(first_photo.order, 1)
