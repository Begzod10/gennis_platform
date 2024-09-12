from rest_framework_simplejwt.authentication import JWTAuthentication


def get_user(request):
    jwt_auth = JWTAuthentication()
    header = request.META.get('HTTP_AUTHORIZATION')
    if header is not None:
        raw_token = header.split(' ')[1]
        validated_token = jwt_auth.get_validated_token(raw_token)
        user_id = validated_token['user_id']
    return user_id
