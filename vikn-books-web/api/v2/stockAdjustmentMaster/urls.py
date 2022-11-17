from django.conf.urls import url,include
from api.v2.stockAdjustmentMaster import views


urlpatterns = [
	url(r'^create-stockAdjustmentMaster/$', views.create_stockAdjustmentMaster, name='create_stockAdjustmentMaster'),
    url(r'^list/stockAdjustmentMaster/$', views.list_stockAdjustmentMaster, name='list_stockAdjustmentMaster'),
    url(r'^view/stockAdjustmentMaster/(?P<pk>.*)/$', views.stockAdjustmentMaster, name='stockAdjustmentMaster'),
    url(r'^edit/stockAdjustmentMaster/(?P<pk>.*)/$', views.edit_stockAdjustmentMaster, name='edit_stockAdjustmentMaster'),
    url(r'^delete/stockAdjustmentMaster/(?P<pk>.*)/$', views.delete_stockAdjustmentMaster, name='delete_stockAdjustmentMaster'),
]