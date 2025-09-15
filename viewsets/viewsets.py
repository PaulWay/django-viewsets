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

from inspect import signature

from django.forms.utils import pretty_name
from django.utils.decorators import classonlymethod
from django.views.generic import View

"""
    Alternate idea from Raphael Gaschinard at PyCon AU 2024 - any method that
    has 'request' as its first argument is going to be considered as a view
    method.  Then the presence of the

    def view_detail_param(self, view):
        " ""
        If the given view is a detail view, it has a named parameter after the
        'request' parameter.
        " ""
        sig = signature(view)
        if 'request' not in sig.parameters:
            return None
        found_request = False
        # Assumes we step through parameters in given order
        for param, pval in sig.parameters.items():
            if found_request:
                # next parameter is detail parameter
                return pval
            if param == 'request':
                found_request = True
        return False

"""

"""
Alternate ideas from FunkyBob:

Try to work with Django's generic class-based views as much as possible, by
supporting interface methods like get_object(), get_queryset(), and so on.

I'm still struggling with this, because Django's CBGVs are based on providing
methods for each HTTP verb ('get', 'post', etc) and I am trying to provide
methods named for the paths they handle (with 'index' and 'detail' being
special).

Certainly I think trying to provide the same helper method interfaces - having
a 'get_X' to override a 'X' attribute in the class, for example.

"""

def action(detail=False, url_path=None, url_name=None, **kwargs):
    """
    Decorate a ViewSet method with this decorator and it will be added to the
    list of endpoints that the ViewSet allows HTTP access to.

    If the 'detail' parameter is set to True, then the generated URL includes
    the viewset's lookup keyword.

    Liberally copied from DRF's @action decorator.

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
    def decorator(func):
        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = url_name if url_name else func.__name__.replace('_', '-')

        func.kwargs = kwargs
        if 'name' not in kwargs:
            func.kwargs['name'] = pretty_name(func.__name__)
        func.kwargs['description'] = func.__doc__

        # Add this view to its class's actions list.
        func.__self__.__class__._actions.append(func)

        return func
    return decorator


class ViewSetMixin:
    """
    Viewsets implement a collection of views all based on a common URL path.

    The main mechanism of working with a ViewSet is to define views using the
    '@action' decorator above, and then to use:

    `path(r'^path/', include(ThisViewSet.get_urls())),`

    In the `urls.py` to include all the URLs handled by that ViewSet.
    """
    lookup_field = 'pk'
    _actions = []
    base_path = ''

    def get_base_path(self, base_path=None):
        """
        Return the base path, or default for class.
        """
        if base_path is not None:
            return base_path
        return self.base_path

    def get_template_name(self, view, base_path):
        """
        Determine the template path to use for this view.
        """
        return f"{base_path}/{view.name}.html"

    def get_detail_param_path(self, view):
        """
        Determine how to represent the detail parameter in the URL path
        """
        # Should this be in the ModelViewSet?
        # if not hasattr(self, '_param_url_type'):
        # return f"<>"
        return NotImplementedError(
            "View parameters are not handled"
        )

    def get_view_path(self, view, base_path):
        """
        Resolve the view path for urls.py
        """
        # Trailing slash handling?
        if view.detail:
            if view.name == 'detail':
                view_path = ''
            else:
                view_path = view.url_path
            return f"^{base_path}/{view_path}"
        else:
            if view.name == 'index':
                view_path = ''
            else:
                view_path = view.url_path
            detail_param = self.get_detail_param_path(view)
            return f"^{base_path}/{detail_param}/{view_path}"

    def get_view_wrapper(self, view, base_path):
        """
        The bit that does the real work - similar to `as_view` in Django's
        generic view classes.  Returns a function that will be called when
        this URL is requested.  This:
        - gets the default context for this viewset
        - updates that with the context from the called view method
        - determines the template for this view
        - returns render_to_response(template, context)
        """
        def wrapper(self, request, *args, **kwargs):
            context = self.get_view_context()
            context.update(view(request, *args, **kwargs))
            template = self.get_template_name(view, base_path)
            return render(request, template, context)

    def get_urls(self):
        """
        Return a valid list of paths for Django to use in an 'include' URL
        definition.
        """
        base_path = self.get_base_path()
        return [
            path(
                self.get_view_path(view, base_path),
                self.get_response(view, base_path)
                name=self.get_view_name(view)
            ),
            for view in self._actions
        ]


class ViewSet(ViewSetMixin):
    """
    Standard view starts with just the index.
    """

    def index(self, request):
        return {
            'context': request
        }


class ModelViewSet(ViewSetMixin):
    """

    """
