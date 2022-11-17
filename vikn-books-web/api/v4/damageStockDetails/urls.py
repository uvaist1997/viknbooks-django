from django.conf.urls import url, include
from api.v4.damageStockDetails import views


urlpatterns = [
    # url(r'^create-damageStockDetails/$', views.create_damageStockDetails, name='create_damageStockDetails'),
    url(r'^create-damageStock/$', views.create_damageStock,
        name='create_damageStock'),
    url(r'^list/damageStockDetails/$', views.list_damageStockDetails,
        name='list_damageStockDetails'),
    url(r'^view/damageStockDetails/(?P<pk>.*)/$',
        views.damageStockDetails, name='damageStockDetails'),
    url(r'^edit/damageStockDetails/(?P<pk>.*)/$',
        views.edit_damageStockDetails, name='edit_damageStockDetails'),
    url(r'^delete/damageStockDetails/(?P<pk>.*)/$',
        views.delete_damageStockDetails, name='delete_damageStockDetails'),

    url(r'^create-damageStockDetailsDummy/$',
        views.create_damageStockDetailsDummy, name='create_damageStockDetailsDummy'),
    url(r'^list/damageStockDetailsDummy/$',
        views.list_damageStockDetailsDummy, name='list_damageStockDetailsDummy'),
    url(r'^edit/damageStockDetailsDummy/(?P<pk>.*)/$',
        views.edit_damageStockDetailsDummy, name='edit_damageStockDetailsDummy'),
    url(r'^delete/damageStockDetailsDummy/(?P<pk>.*)/$',
        views.delete_damageStockDetailsDummy, name='delete_damageStockDetailsDummy'),

    url(r'^create-DummyforEditDamageStock/$',
        views.create_DummyforEditDamageStock, name='create_DummyforEditDamageStock'),
]
