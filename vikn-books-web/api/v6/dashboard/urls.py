from django.conf.urls import url, include
from api.v6.dashboard import views


urlpatterns = [
    url(r'^customer/$', views.customer, name='customer'),
    url(r'^supplier/$', views.supplier, name='supplier'),
    url(r'^accounts/$', views.accounts, name='accounts'),
    url(r'^profit-and-loss/$', views.profit_and_loss, name='profit_and_loss'),
]
