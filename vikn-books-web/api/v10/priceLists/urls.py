from django.conf.urls import url, include
from api.v10.priceLists import views


urlpatterns = [
    url(r'^create-priceList/$', views.create_priceList, name='create_priceList'),
    url(r'^priceLists/$', views.priceLists, name='priceLists'),
    url(r'^view/priceList/(?P<pk>.*)/$', views.priceList, name='priceList'),
    url(r'^edit/priceList/(?P<pk>.*)/$',
        views.edit_priceList, name='edit_priceList'),
    url(r'^delete/priceList/(?P<pk>.*)/$',
        views.delete_priceList, name='delete_priceList'),
    url(r'^single-priceList/$', views.single_priceList, name='single_priceList'),
    url(r'^get-list-byBatchcode/$', views.get_list_byBatchcode,
        name='get_list_byBatchcode'),
    url(r'^single-priceList/batch/$', views.single_priceList_batch, name='single_priceList_batch'),
]
