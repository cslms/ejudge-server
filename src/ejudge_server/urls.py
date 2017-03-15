"""ejudge_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from ejudge_server.views import profile_view, root_view

schema_view = get_schema_view(title='Ejudge server')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'io/', include('ejudge_server.question_io.urls', namespace='io')),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^accounts/profile/$', profile_view),
    url(r'^schema/$', schema_view, name='schema'),
    url(r'^$', root_view, name='root'),
]
