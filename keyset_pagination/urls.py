from django.conf.urls import url
from keyset_pagination.views import Index
urlpatterns = [
    url(r'$', Index.as_view())
]