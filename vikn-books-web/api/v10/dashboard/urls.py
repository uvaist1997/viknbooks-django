from django.conf.urls import url, include
from api.v10.dashboard import views


urlpatterns = [
    url(r'^customer/$', views.customer, name='customer'),
    url(r'^supplier/$', views.supplier, name='supplier'),
    url(r'^accounts/$', views.accounts, name='accounts'),
    url(r'^profit-and-loss/$', views.profit_and_loss, name='profit_and_loss'),
    
    url(r'^dashboard-card/$', views.dashboard_card, name='dashboard_card'),
    url(r'^dashboard-expense/$', views.dashboard_expense, name='dashboard_expense'),
    
]
