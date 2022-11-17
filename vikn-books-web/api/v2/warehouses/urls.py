from django.conf.urls import url,include
from api.v2.warehouses import views


urlpatterns = [
	url(r'^create-warehouse/$', views.create_warehouse, name='create_warehouse'),
    url(r'^warehouses/$', views.warehouses, name='warehouses'),
    url(r'^view/warehouse/(?P<pk>.*)/$', views.warehouse, name='warehouse'),
    url(r'^edit/warehouses/(?P<pk>.*)/$', views.edit_warehouse, name='edit_warehouse'),
    url(r'^delete/warehouse/(?P<pk>.*)/$', views.delete_warehouse, name='delete_warehouse'),
]