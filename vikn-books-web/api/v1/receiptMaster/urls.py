from django.conf.urls import url,include
from api.v1.receiptMaster import views


urlpatterns = [
	url(r'^create-receiptMaster/$', views.create_receiptMaster, name='create_receiptMaster'),
    url(r'^list/receiptMaster/$', views.list_receiptMaster, name='list_receiptMaster'),
    url(r'^view/receiptMaster/(?P<pk>.*)/$', views.receiptMaster, name='receiptMaster'),
    url(r'^edit/receiptMaster/(?P<pk>.*)/$', views.edit_receiptMaster, name='edit_receiptMaster'),
    url(r'^delete/receiptMaster/(?P<pk>.*)/$', views.delete_receiptMaster, name='delete_receiptMaster'),
]