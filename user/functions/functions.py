import jwt

from gennis_platform import settings
from user.serializers import UserSerializerRead, CustomUser


def check_auth(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, {'error': 'Authorization header is missing'}
    token = auth_header.split(' ')[1]

    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')
    except jwt.ExpiredSignatureError:
        return None, {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return None, {'error': 'Invalid token'}

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return None, {'error': 'User not found'}
    return user, None

