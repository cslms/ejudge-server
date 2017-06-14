from django.conf.urls import url, include

from ejudge_server.views import schema_view, api_root_view, index_view
from .question_io import urls as io_urls

urlpatterns = [
    url(r'^api/$', api_root_view, name='api-root'),
    url(r'^api/io/', include(io_urls)),
    url(r'^schema/$', schema_view, name='schema'),
    url(r'^auth/', include('rest_framework.urls', namespace='auth')),
    url(r'^$', index_view, name='index'),
]
