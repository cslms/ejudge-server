from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

#
# Router
#
router = DefaultRouter()
router.root_view_name = 'io-api-root'
router.APIRootView = views.IoView
router.register(r'questions', views.QuestionIoViewSet)
router.register(r'submissions', views.SubmissionIoViewSet)


#
# Patterns
#
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^questions/(?P<pk>[0-9a-f-]+)/iospec/$', views.question_iospec_view),
    url(r'^submissions/(?P<pk>[0-9a-f-]+)/feedback/$',
        views.submission_feedback_view),
]
