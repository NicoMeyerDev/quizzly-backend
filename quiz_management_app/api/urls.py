from rest_framework.routers import DefaultRouter
from .views import QuizViewSet

router = DefaultRouter()
router.register('quizzes', QuizViewSet, basename='quizzes')

urlpatterns = router.urls