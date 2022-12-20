from unittest import TestCase

from viewsets.routers import BaseRouter, SimpleRouter
from viewsets.viewsets import ViewSet, ModelViewSet, action

class TestViewSet(ViewSet):
    template_path_base = ''
    # list and retrieve

class RouterTest(TestCase):
    def test_basic_route(self):
        router = BaseRouter()
        router.register(r'test', TestViewSet)
        self.assertNotNone(router)

# python -m unittest discover
if __name__ == '__main__':
    unittest.main()
