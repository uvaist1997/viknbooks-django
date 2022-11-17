from django.conf.urls import url,include
from api.v1.purchaseReturns import views


urlpatterns = [
	url(r'^create-purchaseReturn/$', views.create_purchaseReturn, name='create_purchaseReturn'),
	url(r'^edit/purchaseReturn/(?P<pk>.*)/$', views.edit_purchaseReturn, name='edit_purchaseReturn'),
    url(r'^list/purchaseReturnMaster/$', views.list_purchaseReturnMaster, name='list_purchaseReturnMaster'),
	url(r'^purchase-return-pagination/$', views.purchase_return_pagination, name='purchase_return_pagination'),
    url(r'^view/purchaseReturnMaster/(?P<pk>.*)/$', views.purchaseReturnMaster, name='purchaseReturnMaster'),
    url(r'^delete/purchaseReturnMaster/(?P<pk>.*)/$', views.delete_purchaseReturnMaster, name='delete_purchaseReturnMaster'),
    url(r'^report/purchaseReturns/$', views.report_purchaseReturns, name='report_purchaseReturns'),
]