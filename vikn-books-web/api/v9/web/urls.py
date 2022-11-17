from django.conf.urls import url, include
from api.v9.web import views


urlpatterns = [
    url(r'^create-contact/$', views.contact, name='contact'),
]
