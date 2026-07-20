from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, OptionViewSet, QuestionTypeViewSet, UserAnswerViewSet, SelectedOptionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'options', OptionViewSet, basename='option')
router.register(r'question-types', QuestionTypeViewSet, basename='questiontype')
router.register(r'answers', UserAnswerViewSet, basename='answer')
router.register(r'selected-options', SelectedOptionViewSet, basename='selectedoption')

urlpatterns = [
    path('', include(router.urls)),
]