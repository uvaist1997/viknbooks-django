from django.conf.urls import url, include
from api.v10.routes import views


urlpatterns = [
    url(r'^create-route/$', views.create_route, name='create_route'),
    url(r'^routes/$', views.routes, name='routes'),
    url(r'^view/route/(?P<pk>.*)/$', views.route, name='route'),
    url(r'^edit/route/(?P<pk>.*)/$', views.edit_route, name='edit_route'),
    url(r'^delete/route/(?P<pk>.*)/$', views.delete_route, name='delete_route'),

    url(r'^search-routes/$', views.search_routes, name='search_routes'),
]
