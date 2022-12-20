from unittest import TestCase

from viewsets.routers import BaseRouter, SimpleRouter
from viewsets.viewsets import ViewSet, action

class SimpleViewSet(ViewSet):
    template_path_base = ''
    # list and retrieve

class RouterTest(TestCase):
    def test_basic_route(self):
        router = BaseRouter()
        self.assertIsNotNone(router)
        # Register with no basename is not implemented in BaseRouter
        with self.assertRaises(NotImplementedError):
            router.register(r'test', SimpleViewSet)
        router.register(r'test', SimpleViewSet, basename='test')
        # BaseRouter does not implement a way to get the URLs
        with self.assertRaises(NotImplementedError):
            router.urls

# python -m unittest discover
if __name__ == '__main__':
    unittest.main()
