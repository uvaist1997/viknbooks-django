from django.conf.urls import url, include
from api.v3.purchaseReturnMaster import views


urlpatterns = [
    url(r'^create-purchaseReturnMaster/$',
        views.create_purchaseReturnMaster, name='create_purchaseReturnMaster'),
    url(r'^list/purchaseReturnMaster/$', views.list_purchaseReturnMaster,
        name='list_purchaseReturnMaster'),
    url(r'^view/purchaseReturnMaster/(?P<pk>.*)/$',
        views.purchaseReturnMaster, name='purchaseReturnMaster'),
    url(r'^edit/purchaseReturnMaster/(?P<pk>.*)/$',
        views.edit_purchaseReturnMaster, name='edit_purchaseReturnMaster'),
    url(r'^delete/purchaseReturnMaster/(?P<pk>.*)/$',
        views.delete_purchaseReturnMaster, name='delete_purchaseReturnMaster'),
]
