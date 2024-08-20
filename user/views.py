import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from permissions.functions.CheckUserPermissions import check_user_permissions


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def get_user_from_refresh_token(self, refresh_token):
        try:
            decoded_data = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = decoded_data.get("user_id")

            CustomUser = get_user_model()
            user = CustomUser.objects.get(id=user_id)
            return user, None
        except jwt.ExpiredSignatureError:
            return None, {"detail": "Refresh token has expired."}
        except jwt.InvalidTokenError:
            return None, {"detail": "Invalid refresh token."}
        except ObjectDoesNotExist:
            return None, {"detail": "User not found."}

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        user, auth_error = self.get_user_from_refresh_token(refresh_token)

        if auth_error:
            return Response(auth_error, status=status.HTTP_401_UNAUTHORIZED)

        table_names = ['teacherattendance', 'teacher', 'system']
        permissions = check_user_permissions(user, table_names)

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        access_token = serializer.validated_data.get('access')

        response_data = {
            'access': access_token,
            'permissions': permissions
        }

        return Response(response_data, status=status.HTTP_200_OK)
