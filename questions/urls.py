from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, PropositionViewSet, TypeQuestionViewSet, ReponseUtilisateurViewSet, PropositionSelectionneeViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'propositions', PropositionViewSet, basename='proposition')
router.register(r'types-question', TypeQuestionViewSet, basename='typequestion')
router.register(r'reponses', ReponseUtilisateurViewSet, basename='reponse')
router.register(r'propositions-selectionnees', PropositionSelectionneeViewSet, basename='proposition-selectionnee')

urlpatterns = [
    path('', include(router.urls)),
]