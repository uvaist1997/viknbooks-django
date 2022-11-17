from django.conf.urls import url, include
from api.v6.stockAdjustments import views


urlpatterns = [
    url(r'^create-stockAdjustment/$', views.create_stockAdjustment,
        name='create_stockAdjustment'),
    url(r'^edit/stockAdjustment/(?P<pk>.*)/$',
        views.edit_stockAdjustment, name='edit_stockAdjustment'),
    url(r'^list/stockAdjustmentMaster/$', views.list_stockAdjustmentMaster,
        name='list_stockAdjustmentMaster'),
    url(r'^view/stockAdjustmentMaster/(?P<pk>.*)/$',
        views.stockAdjustmentMaster, name='stockAdjustmentMaster'),
    url(r'^delete/stockAdjustmentDetails/(?P<pk>.*)/$',
        views.delete_stockAdjustmentDetails, name='delete_stockAdjustmentDetails'),
    url(r'^delete/stockAdjustmentMaster/(?P<pk>.*)/$',
        views.delete_stockAdjustmentMaster, name='delete_stockAdjustmentMaster'),
]
