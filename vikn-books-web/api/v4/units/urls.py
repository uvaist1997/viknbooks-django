from django.conf.urls import url, include
from api.v4.units import views


urlpatterns = [
    url(r'^create-unit/$', views.create_unit, name='create_unit'),
    url(r'^units/$', views.units, name='units'),
    url(r'^view/unit/(?P<pk>.*)/$', views.unit, name='unit'),
    url(r'^edit/unit/(?P<pk>.*)/$', views.edit_unit, name='edit_unit'),
    url(r'^delete/unit/(?P<pk>.*)/$', views.delete_unit, name='delete_unit'),

    url(r'^search-units/$', views.search_units, name='search_units'),
]
