from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, PropositionViewSet, TypeQuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'propositions', PropositionViewSet, basename='proposition')
router.register(r'types-question', TypeQuestionViewSet, basename='typequestion')

urlpatterns = [
    path('', include(router.urls)),
]