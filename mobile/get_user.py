from rest_framework_simplejwt.authentication import JWTAuthentication


def get_user(request):
    jwt_auth = JWTAuthentication()
    header = request.META.get('HTTP_AUTHORIZATION')
    user_id = None  # default qiymat
    if header is not None:
        try:
            raw_token = header.split(' ')[1]
            validated_token = jwt_auth.get_validated_token(raw_token)
            user_id = validated_token.get('user_id')
        except Exception as e:
            # token noto‘g‘ri bo‘lsa ham None qaytadi
            user_id = None
    return user_id
