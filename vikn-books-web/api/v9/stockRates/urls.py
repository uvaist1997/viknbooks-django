from django.conf.urls import url, include
from api.v9.stockRates import views


urlpatterns = [
    url(r'^create-stockRate/$', views.create_stockRate, name='create_stockRate'),
    url(r'^stockRates/$', views.stockRates, name='stockRates'),
    url(r'^view/stockRate/(?P<pk>.*)/$', views.stockRate, name='stockRate'),
    url(r'^edit/stockRate/(?P<pk>.*)/$',
        views.edit_stockRate, name='edit_stockRate'),
    url(r'^delete/stockRate/(?P<pk>.*)/$',
        views.delete_stockRate, name='delete_stockRate'),
]
