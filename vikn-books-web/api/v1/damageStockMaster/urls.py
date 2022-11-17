from django.conf.urls import url,include
from api.v1.damageStockMaster import views


urlpatterns = [
	url(r'^create-damageStockMaster/$', views.create_damageStockMaster, name='create_damageStockMaster'),
    url(r'^list/damageStockMaster/$', views.list_damageStockMaster, name='list_damageStockMaster'),
    url(r'^view/damageStockMaster/(?P<pk>.*)/$', views.damageStockMaster, name='damageStockMaster'),
    url(r'^edit/damageStockMaster/(?P<pk>.*)/$', views.edit_damageStockMaster, name='edit_damageStockMaster'),
    url(r'^delete/damageStockMaster/(?P<pk>.*)/$', views.delete_damageStockMaster, name='delete_damageStockMaster'),
]