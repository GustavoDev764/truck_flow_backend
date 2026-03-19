"""Views de autenticação: login (JWT) e dados do usuário atual."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import CurrentUserSerializer, CustomTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    """Login retorna access + refresh + user (id, username, groups)."""

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserAPIView(APIView):
    """Retorna dados do usuário autenticado (id, username, groups, is_manage)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)
