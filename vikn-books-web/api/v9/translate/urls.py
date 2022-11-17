from django.conf.urls import include, url

from api.v9.translate import views

urlpatterns = [
    url(r"^translate/$", views.translate, name="translate"),
]
