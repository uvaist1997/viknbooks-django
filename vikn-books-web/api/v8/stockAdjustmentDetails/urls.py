from django.conf.urls import url, include
from api.v8.stockAdjustmentDetails import views


urlpatterns = [
    url(r'^create-stockAdjustmentDetails/$',
        views.create_stockAdjustmentDetails, name='create_stockAdjustmentDetails'),
    url(r'^list/stockAdjustmentDetails/$',
        views.list_stockAdjustmentDetails, name='list_stockAdjustmentDetails'),
    url(r'^view/stockAdjustmentDetails/(?P<pk>.*)/$',
        views.stockAdjustmentDetails, name='stockAdjustmentDetails'),
    url(r'^edit/stockAdjustmentDetails/(?P<pk>.*)/$',
        views.edit_stockAdjustmentDetails, name='edit_stockAdjustmentDetails'),
    url(r'^delete/stockAdjustmentDetails/(?P<pk>.*)/$',
        views.delete_stockAdjustmentDetails, name='delete_stockAdjustmentDetails'),

    url(r'^create-stockAdjustmentDetailsDummy/$',
        views.create_stockAdjustmentDetailsDummy, name='create_stockAdjustmentDetailsDummy'),
    url(r'^list/stockAdjustmentDetailsDummy/$',
        views.list_stockAdjustmentDetailsDummy, name='list_stockAdjustmentDetailsDummy'),
    url(r'^edit/stockAdjustmentDetailsDummy/(?P<pk>.*)/$',
        views.edit_stockAdjustmentDetailsDummy, name='edit_stockAdjustmentDetailsDummy'),
    url(r'^delete/stockAdjustmentDetailsDummy/(?P<pk>.*)/$',
        views.delete_stockAdjustmentDetailsDummy, name='delete_stockAdjustmentDetailsDummy'),

    url(r'^create-DummyforEditStockAdjustmentMaster/$',
        views.create_DummyforEditStockAdjustmentMaster, name='create_DummyforEditStockAdjustmentMaster'),
]
