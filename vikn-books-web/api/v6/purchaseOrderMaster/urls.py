from django.conf.urls import url, include
from api.v6.purchaseOrderMaster import views


urlpatterns = [
    url(r'^create-purchaseOrderMaster/$', views.create_purchaseOrderMaster,
        name='create_purchaseOrderMaster'),
    url(r'^list/purchaseOrderMaster/$', views.list_purchaseOrderMaster,
        name='list_purchaseOrderMaster'),
    url(r'^view/purchaseOrderMaster/(?P<pk>.*)/$',
        views.purchaseOrderMaster, name='purchaseOrderMaster'),
    url(r'^edit/purchaseOrderMaster/(?P<pk>.*)/$',
        views.edit_purchaseOrderMaster, name='edit_purchaseOrderMaster'),
    url(r'^delete/purchaseOrderMaster/(?P<pk>.*)/$',
        views.delete_purchaseOrderMaster, name='delete_purchaseOrderMaster'),
]
