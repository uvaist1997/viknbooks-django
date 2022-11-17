from django.conf.urls import url,include
from api.v2.brands import views


urlpatterns = [
	url(r'^create-brand/$', views.create_brand, name='create_brand'),
    url(r'^brands/$', views.brands, name='brands'),
    url(r'^view/brand/(?P<pk>.*)/$', views.brand, name='brand'),
    url(r'^edit/brand/(?P<pk>.*)/$', views.edit_brand, name='edit_brand'),
    url(r'^delete/brand/(?P<pk>.*)/$', views.delete_brand, name='delete_brand'),

    url(r'^torunqryBillDiscAmt/$', views.torunqryBillDiscAmt, name='torunqryBillDiscAmt'),
    url(r'^torunqry/$', views.torunqry, name='torunqry'),
    url(r'^torunqryPurchase/$', views.torunqryPurchase, name='torunqryPurchase'),
    url(r'^torunqryOpeningStock/$', views.torunqryOpeningStock, name='torunqryOpeningStock'),
    url(r'^torunqryPyment/$', views.torunqryPyment, name='torunqryPyment'),
    url(r'^torunqryReciept/$', views.torunqryReciept, name='torunqryReciept'),

    url(r'^torunqryTest/$', views.torunqryTest, name='torunqryTest'),
    url(r'^torunqryForPriceList/$', views.torunqryForPriceList, name='torunqryForPriceList'),
    url(r'^torunqryProductUpdate/$', views.torunqryProductUpdate, name='torunqryProductUpdate'),
]