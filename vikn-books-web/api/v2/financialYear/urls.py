from django.conf.urls import url,include
from api.v2.financialYear import views


urlpatterns = [
	url(r'^create-financial-year/$', views.create_financial_year, name='create_financial_year'),
    url(r'^financial-years/$', views.financial_years, name='financial_years'),
    url(r'^view/financial-year/(?P<pk>.*)/$', views.financial_year, name='financial_year'),
    url(r'^edit/financial-year/(?P<pk>.*)/$', views.edit_financial_year, name='edit_financial_year'),
    url(r'^delete/financial-year/(?P<pk>.*)/$', views.delete_financial_year, name='delete_financial_year'),
]