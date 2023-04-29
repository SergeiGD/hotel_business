from hotel_business_module.tests.base_test import BaseTest
from hotel_business_module.gateways.tags_gateway import TagsGateway
from hotel_business_module.models.tags import Tag
from hotel_business_module.tests.session import get_session


class TestTags(BaseTest):
    def test_crud(self):
        with get_session() as session:
            tag = Tag(name='test_tag')
            TagsGateway.save_tag(tag, session)

            self.assertIsNotNone(TagsGateway.get_by_id(tag.id, session))
