from django.conf.urls import url
from sample.views import Index
urlpatterns = [
    url(r'$', Index.as_view())
]