from django.conf.urls import url,include
from api.v2.translate import views


urlpatterns = [
    url(r'^translate/$', views.translate, name='translate'),
]