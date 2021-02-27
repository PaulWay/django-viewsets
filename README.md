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

```python
### models.py ###
from django.db import models

class BlogPost(models.Model):
    slug = models.SlugField()
    title = models.CharField()
    text = models.TextField()

### views.py ###
from my_site.models import BlogPost
from django_viewsets.decorators import action
from django_viewsets import ViewSet, ModelViewSet

class HomePage(ViewSet):
    template_dir = 'home'

    def index(self, request):
        return self.render()

class BlogViewSet(ModelViewSet):
    lookup = 'slug'
    queryset = BlogPost.objects.all()
    template_dir = 'home/blog'

    # list, detail, create, destroy already included

    @action(detail=True)
    def stats(self, request, slug):
        post = self.get_object(slug=slug)
        # render assumes template = action name otherwise:
        return self.render(post, template='blog_stats')

```

