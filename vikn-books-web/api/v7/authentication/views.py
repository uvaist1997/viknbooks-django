from rest_framework_simplejwt.views import TokenObtainPairView
from api.v7.authentication.serializers import UserTokenObtainPairSerializer


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
