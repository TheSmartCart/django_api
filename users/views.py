from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        """Autorise tout le monde à s'inscrire, mais protège les autres actions."""
        if self.action in ['create', 'token', 'token_refresh']:
            return [AllowAny()]
        return [IsAuthenticated()] 