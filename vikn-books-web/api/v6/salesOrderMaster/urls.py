from django.conf.urls import url, include
from api.v6.salesOrderMaster import views


urlpatterns = [
    url(r'^create-salesOrderMaster/$', views.create_salesOrderMaster,
        name='create_salesOrderMaster'),
    url(r'^list/salesOrderMaster/$', views.list_salesOrderMaster,
        name='list_salesOrderMaster'),
    url(r'^view/salesOrderMaster/(?P<pk>.*)/$',
        views.salesOrderMaster, name='salesOrderMaster'),
    url(r'^edit/salesOrderMaster/(?P<pk>.*)/$',
        views.edit_salesOrderMaster, name='edit_salesOrderMaster'),
    url(r'^delete/salesOrderMaster/(?P<pk>.*)/$',
        views.delete_salesOrderMaster, name='delete_salesOrderMaster'),
]
