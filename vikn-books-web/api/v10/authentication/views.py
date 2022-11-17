from rest_framework_simplejwt.views import TokenObtainPairView

from api.v10.authentication.serializers import UserTokenObtainPairSerializer


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
