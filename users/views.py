from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        partial = True
        serializer = self.get_serializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_permissions(self):
        """Autorise tout le monde à s'inscrire, mais protège les autres actions."""
        if self.action in ['create', 'token', 'token_refresh']:
            return [AllowAny()]
        return [IsAuthenticated()] 