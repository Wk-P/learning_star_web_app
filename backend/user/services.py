from .models import User
from serializers import UserSerializer


def get_user_list():
    users = User.objects.all()
    data = UserSerializer(users, many=True).data

    return data



def get_user(pk: int):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return None
    
    data = UserSerializer(user).data

    return data