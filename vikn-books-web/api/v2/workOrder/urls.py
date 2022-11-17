from django.conf.urls import url,include
from api.v2.workOrder import views


urlpatterns = [
	url(r'^create-workOrder/$', views.create_workOrder, name='create_workOrder'),
	# url(r'^edit/purchase/(?P<pk>.*)/$', views.edit_purchase, name='edit_purchase'),
 #    url(r'^list/purchaseMaster/$', views.list_purchaseMaster, name='list_purchaseMaster'),
 #   	url(r'^purchase-pagination/$', views.purchase_pagination, name='purchase_pagination'),
 #    url(r'^view/purchaseMaster/(?P<pk>.*)/$', views.purchaseMaster, name='purchaseMaster'),
 #    # url(r'^delete/purchaseDetails/(?P<pk>.*)/$', views.delete_purchaseDetails, name='delete_purchaseDetails'),
 #    url(r'^delete/purchaseMaster/(?P<pk>.*)/$', views.delete_purchaseMaster, name='delete_purchaseMaster'),

 #    url(r'^purchaseInvoice-for-purchaseReturn/$', views.purchaseInvoice_for_PurchaseReturn, name='purchaseInvoice_for_PurchaseReturn'),

 #    url(r'^report/purchases/$', views.report_purchases, name='report_purchases'),

 #    url(r'^default-values/$', views.default_values, name='default_values'),
]