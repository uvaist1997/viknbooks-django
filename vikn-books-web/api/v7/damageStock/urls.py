from django.conf.urls import url, include
from api.v7.damageStock import views


urlpatterns = [
    url(r'^create-damageStock/$', views.create_damageStock,
        name='create_damageStock'),
    url(r'^edit/damageStock/(?P<pk>.*)/$',
        views.edit_damageStock, name='edit_damageStock'),
    url(r'^view/damageStock/(?P<pk>.*)/$',
        views.damageStockMaster, name='damageStockMaster'),
    url(r'^list/damageStock/$', views.list_damageStockMaster,
        name='list_damageStockMaster'),
    url(r'^delete/damageStockDetails/(?P<pk>.*)/$',
        views.delete_damageStockDetails, name='delete_damageStockDetails'),
    url(r'^delete/damageStock/(?P<pk>.*)/$',
        views.delete_damageStockMaster, name='delete_damageStockMaster'),
]
