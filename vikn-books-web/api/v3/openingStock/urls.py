from django.conf.urls import url, include
from api.v3.openingStock import views


urlpatterns = [
    url(r'^create-openingStock/$', views.create_openingStock,
        name='create_openingStock'),
    url(r'^edit/openingStock/(?P<pk>.*)/$',
        views.edit_openingStock, name='edit_openingStock'),
    url(r'^openingStocks/$', views.openingStocks, name='openingStocks'),
    url(r'^opening-stock-pagination/$', views.opening_stock_pagination,
        name='opening_stock_pagination'),
    url(r'^view/openingStock/(?P<pk>.*)/$',
        views.openingStock, name='openingStock'),
    url(r'^delete/openingStockDetails/(?P<pk>.*)/$',
        views.delete_openingStockDetails, name='delete_openingStockDetails'),
    url(r'^delete/openingStockMaster/(?P<pk>.*)/$',
        views.delete_openingStockMaster, name='delete_openingStockMaster'),
]
