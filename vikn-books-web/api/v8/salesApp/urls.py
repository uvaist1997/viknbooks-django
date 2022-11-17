from django.conf.urls import url, include
from api.v8.salesApp import views


urlpatterns = [
url(r'^salesApp-companies/$', views.salesApp_companies, name='salesApp_companies'),
url(r'^pos-product-list/$', views.pos_product_list, name='pos_product_list'),
url(r'^pos-product-search/$', views.pos_product_search, name='pos_product_search'),
url(r'^pos-parties/$', views.pos_parties, name='pos_parties'),
url(r'^salesApp-login/$', views.salesApp_login, name='salesApp_login'),
]
