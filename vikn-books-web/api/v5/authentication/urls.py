from django.urls import path, re_path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from api.v5.authentication import views


urlpatterns = [
    path('token/', views.UserTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
