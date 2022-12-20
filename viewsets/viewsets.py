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

from django.forms.utils import pretty_name
from django.view.generic import View



def action(methods=None, detail=False, url_path=None, url_name=None, **kwargs):
    """
    Decorate a ViewSet method with this decorator and it will be added to the
    list of endpoints that the ViewSet allows HTTP access to.

    If the 'detail' parameter is set to True, then the generated URL includes
    the viewset's lookup keyword.

    Liberally copied from DRF's @action decorator.

    :param methods: a list of HTTP methods that action responds to.
        Defaults to GET only.
    :param detail: whether this action applies to instance (detail) requests.  If
        `False`, it applies to collection (list) requests.
    :param url_path: The URL segment for this action, defaulting to the
        decorated method name.
    :param url_name: The internal URL name for this action, for `reverse()`.
        Defaults to the name of the decorated method, with underscores
        replaced by dashes.
    :param kwargs: Additional properties to set on this view.  This is used
        to override viewset-level settings (if any).
    """
    methods = ['get'] if methods is None else methods
    methods = [method.lower for method in methods]

    def decorator(func):
        # Was: func.mapping = MethodMapper(func, methods)
        func.mapping = {
            method: func.__name__
            for method in methods
        }
        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = url_name if url_name else func.__name__.replace('_', '-')

        func.kwargs = kwargs
        if 'name' not in kwargs:
            func.kwargs['name'] = pretty_name(func.__name__)
        func.kwargs['description'] = func.__doc__

        return func
    return decorator


class ViewSetMixin:
    """
    The basic ViewSet mixin provides the mapping from instance methods in the
    class to names that appear in the URLs handled by this ViewSet.
    """

    __endpoints = list()

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        """
        Select the view function from the methods this viewset supports.
        This is different from the standard View class `as_view` method,
        ...
        """
        # Borrowing liberally from DRF's viewsets.py
        cls.name = None
        cls.description = None
        cls.basename = None
        if not actions:
            raise TypeError(
                "The `actions` argument must be provided when calling "
                "`.as_view()` on a ViewSet, as a dictionary mapping HTTP "
                "methods (in lower case) to the viewset methods to handle them"
            )
        # sanitise keyword arguments, as per viewsets.py
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    "You should not pass in the %s method name as a "
                    "keyword to %s()" % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError(
                    "%s() received an invalid keyword %r" % (cls.__name__, key)
                )

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if 'get' in actions and 'head' not in actions:
                actions['head'] = actions['get']
            self.action_map = actions
            # Bind HTTP methods to class methods
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method, handler)
            self.request = request
            self.args = args
            self.kargs = kwargs
            return self.dispatch(request, *args, **kwargs)

        update_wrapper(view, cls, updated=())
        update_wrapper(view, cls.dispatch, assigned=())
        view.cls = cls
        view.initkwargs = initkwargs
        view.actions = actions
        return csrf_exempt(view)


class ViewSet(View, ViewSetMixin):
    pass
