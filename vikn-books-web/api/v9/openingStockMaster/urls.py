from django.conf.urls import url, include
from api.v9.openingStockMaster import views


urlpatterns = [
    url(r'^create-openingStockMaster/$', views.create_openingStockMaster,
        name='create_openingStockMaster'),
    url(r'^openingStockMasters/$', views.openingStockMasters,
        name='openingStockMasters'),
    url(r'^view/openingStockMaster/(?P<pk>.*)/$',
        views.openingStockMaster, name='openingStockMaster'),
    url(r'^edit/openingStockMaster/(?P<pk>.*)/$',
        views.edit_openingStockMaster, name='edit_openingStockMaster'),
    url(r'^delete/openingStockMaster/(?P<pk>.*)/$',
        views.delete_openingStockMaster, name='delete_openingStockMaster'),
]
