from unittest.mock import Mock
from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.tags_gateway import TagsGateway
from hotel_business_module.models.tags import Tag
from hotel_business_module.tests.session import get_session


class TestTags(BaseTest):
    def test_save(self):
        """
        Тестирование сохранения тегов
        """
        with get_session() as session:
            tag = Tag(name='test_tag')
            # сохраняем тег
            TagsGateway.save_tag(tag, session)

            # проверяем сохранился ли
            self.assertIsNotNone(TagsGateway.get_by_id(tag.id, session))

            # создаем тег с таким же названием
            dup_tag = Tag(name='test_tag')

            # проверяем, чтоб вернул ошибку
            self.assertRaises(ValueError, TagsGateway.save_tag, dup_tag, session)
            # проверяем, что не сохранил
            self.assertIsNone(dup_tag.id)

    def test_delete(self):
        """
        Тестирование удаления тега
        """
        with get_session() as session:
            tag = Tag(name='test_tag')
            # сохраняем
            TagsGateway.save_tag(tag, session)
            tag_id = tag.id
            # удаляем
            TagsGateway.delete_tag(tag, session)
            # проверяем, что удалился
            self.assertIsNone(TagsGateway.get_by_id(tag_id, session))

    def test_get(self):
        """
        Тестирование получения списка тегов
        """
        with get_session() as session:
            tag = Tag(name='test_tag')
            tag2 = Tag(name='test_tag2')
            # сохраняем
            TagsGateway.save_tag(tag, session)
            TagsGateway.save_tag(tag2, session)
            # проверяем, что все вернул
            self.assertEqual(TagsGateway.get_all(session), [tag, tag2])
