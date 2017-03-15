from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from ejudge_server.question_io import views

router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router.register(r'graders', views.GraderViewSet)
router.register(r'jobs', views.GradingJobViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
