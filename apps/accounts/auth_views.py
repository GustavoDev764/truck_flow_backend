"""Views de autenticação: login (JWT), logout e dados do usuário atual."""

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import CurrentUserSerializer, CustomTokenObtainPairSerializer
from apps.accounts.services.session_service import revoke_session_by_jti


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


class LogoutView(APIView):
    """Invalida o token atual (revoga sessão). Requer token no header Authorization."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Bearer "):
            token_str = auth_header[7:]
            try:
                from rest_framework_simplejwt.tokens import AccessToken

                access_token = AccessToken(token_str)
                jti = access_token.get("jti")
                if jti:
                    revoke_session_by_jti(jti)
            except Exception:
                pass
        return Response(status=HTTP_204_NO_CONTENT)
