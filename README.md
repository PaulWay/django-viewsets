# django-viewsets
A different way of constructing Django class-based views

Django's class based views provide many advantages over 'traditional' function
based views.  They simplify the handling of different HTTP methods and do much
of the work in setting up and handling forms.

But the downside is that each class basically handles only one endpoint.  You
then have to stitch them together in the `urls` file.  And the names of the
endpoints there kind of look like the names of your classes.  It almost seems
like... repeating yourself.

Now, Django REST Framework has the concept of a `ViewSet`.  Firstly they
handle the different HTTP methods - handling POST is via a `create` method,
for example.  But they also allow extra views to be annotated as either a
'list' or a 'detail' view, so for instance you can have a `/author/` list
view of all authors, an `/author/sales/` list view of the sales information
for all authors, an `/author/Shakespeare/` detail view of Shakespeare, and an
`/author/Shakespeare/books/` detail view for Shakespeare's publications.
DRF's 'routers' can then introspect the `ViewSet` to find which URLs it
publishes and maps them automatically.

**django-viewsets** provides the best of both worlds for Django users.

# Example:

### models.py ###
```python
from django.db import models

class BlogPost(models.Model):
    slug = models.SlugField()
    title = models.CharField()
    text = models.TextField()
```

### views.py ###
```python
from my_site.models import BlogPost
from viewsets.decorators import action
from viewsets import ViewSet, ModelViewSet

class HomePage(ViewSet):
    """
    A simple handler for the home page index.
    """
    template_dir = 'home'

    def index(self, request):
        return self.render()

class BlogViewSet(ModelViewSet):
    lookup_field = 'slug'
    queryset = BlogPost.objects.all()
    template_dir = 'home/blog'

    # list, detail, create, destroy already included

    @action(detail=True)
    def stats(self, request, slug):
        post = self.get_object(slug=slug)
        # View methods return a context to be sent to the relevant template
        return {
            'mentions': post.mention_set.count()
        }
```

### urls.py ###
```python
from django.conf.urls import path, include
from views import HomePage, BlogViewSet

urlpatterns = [
    path(r'^', include(HomePage.get_urls())),
    path(r'^blog/', include(BlogViewSet.get_urls())),
]
```
