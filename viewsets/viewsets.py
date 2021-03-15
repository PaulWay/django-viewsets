"""
ViewSets are a different style of class-based view that handle all the
access to a particular 'base' URL.  Instead of simply implementing the HTTP
access methods - `get`, `post`, etc - ViewSets implement the path suffixes
to that base URL - `/index`, `/new`, etc.  Simply implement a method and it
becomes a view - the `/new` path corresponds to the `def new(request):`
method.

ViewSets also provide an easy way of implementing a set of views of a
particular object, being 'detail' views as opposed to the 'general' views
given above.  A view decorated with the `@detail` decorator is assumed to
take a parameter that can be used to look up an object.

Typically, rather than instantiate views from viewsets directly, you'll
register the viewset with a router and have the URL patterns be generated
automatically:

    router = DefaultRouter()
    router.register(r'widgets', WidgetViewSet, 'widget')
    urlpatterns = router.urls

This borrows heavily from Django REST Framework's idea of ViewSets.
"""

from inspect import getmembers

class ViewSetMixin:
    """
    """
