"""
Routers are a convenient and consistent way of automatically determining the
URL configuration of your web site.

Simply instantiate a Router class, then register each ViewSet you use with
that router.  For example:

    router = routers.SimpleRouter()
    router.register('blog', BlogViewSet)
    router.register('art', GalleryViewSet, basename='gallery')

    urlpatterns = router.urls

Each ViewSet then describes the paths it serves to the router, and this then
creates the full list of URL patterns.  Essentially this should take the
place of the 'include' pattern of:

    urlpatterns = [
        ...
        path(r'blog', include('blogs.urls')),
    ]

and then having to have the 'blogs' urls.py then list all the paths the
BlogViewSet accepts.
"""

from collections import namedtuple

# Copied and adapted gratefully from Django REST Framework

Route = namedtuple('Route', ['url', 'name', 'detail', 'initkwargs'])


class BaseRouter:
    """
    Mostly copied from DRF...
    """
    def __init__(self):
        self.registry = []

    def register(self, prefix, viewset, basename=None):
        if basename is None:
            basename = self.get_default_basename(viewset)
        self.registry.append((prefix, viewset, basename))

        # invalidate the urls cache
        if hasattr(self, '_urls'):
            del self._urls

    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the viewset.
        """
        raise NotImplementedError('get_default_basename must be overridden')

    def get_urls(self):
        """
        Return a list of URL patterns, given the registered viewsets.
        """
        raise NotImplementedError('get_urls must be overridden')

    @property
    def urls(self):
        if not hasattr(self, '_urls'):
            self._urls = self.get_urls()
        return self._urls


class SimpleRouter(BaseRouter):
    """
    Mostly copied from DRF...
    """

    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
    ]

    def __init__(self, trailing_slash=True):
        self.trailing_slash = '/' if trailing_slash else ''
        super().__init__()

    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the viewset.
        """
        queryset = getattr(viewset, 'queryset', None)

        assert queryset is not None, (
            '`basename` argument not specified, and '
            'could not automatically determine the name from the viewset, as '
            'it does not have a `.queryset` attribute.'
        )

        return queryset.model._meta.object_name.lower()

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """
        # converting to list as iterables are good for one pass, known host
        # needs to be checked again and again for different functions.
        known_actions = list(flatten([
            route.mapping.values()
            for route in self.routes
            if isinstance(route, Route)
        ]))
        extra_actions = viewset.get_extra_actions()

        # checking action names against the known actions list
        not_allowed = [
            action.__name__ for action in extra_actions
            if action.__name__ in known_actions
        ]
        if not_allowed:
            msg = ('Cannot use the @action decorator on the following '
                   'methods, as they are existing routes: %s')
            raise ImproperlyConfigured(msg % ', '.join(not_allowed))

        # partition detail and list actions
        detail_actions = [action for action in extra_actions if action.detail]
        list_actions = [action for action in extra_actions if not action.detail]

        return self.routes

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against a single instance.
        """
        base_regex = '(?P<{lookup_prefix}{lookup_url_kwarg}>{lookup_value})'
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        lookup_url_kwarg = getattr(viewset, 'lookup_url_kwarg', None) or lookup_field
        lookup_value = getattr(viewset, 'lookup_value_regex', '[^/.]+')
        return base_regex.format(
            lookup_prefix=lookup_prefix,
            lookup_url_kwarg=lookup_url_kwarg,
            lookup_value=lookup_value
        )

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                # controlled by project's urls.py and the router is in an app,
                # so a slash in the beginning will (A) cause Django to give
                # warnings and (B) generate URLS that will require using '//'.
                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'basename': basename,
                    'detail': route.detail,
                })

                view = viewset.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)
                ret.append(re_path(regex, view, name=name))

        return ret
