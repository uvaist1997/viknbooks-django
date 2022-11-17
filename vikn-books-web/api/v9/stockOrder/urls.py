from django.conf.urls import url, include
from api.v9.stockOrder import views


urlpatterns = [
    url(r'^create-stockOrder/$', views.create_stockOrder,
        name='create_stockOrder'),
    url(r'^edit/stockOrder/(?P<pk>.*)/$',
        views.edit_stockOrder, name='edit_stockOrder'),
    url(r'^stock-order-pagination/$', views.stock_order_pagination,
        name='stock_order_pagination'),
    url(r'^view/stockOrderMaster/(?P<pk>.*)/$',
        views.stockOrderMasterID, name='stockOrderMasterID'),
    url(r'^delete/stockOrderMaster/(?P<pk>.*)/$',
        views.delete_stockOrderMasterID, name='delete_stockOrderMasterID'),


]
