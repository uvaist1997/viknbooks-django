from django.conf.urls import url, include
from api.v4.productGroups import views


urlpatterns = [
    url(r'^create-productGroup/$', views.create_productGroup,
        name='create_productGroup'),
    url(r'^productGroups/$', views.productGroups, name='productGroups'),
    url(r'^view/productGroup/(?P<pk>.*)/$',
        views.productGroup, name='productGroup'),
    url(r'^edit/productGroup/(?P<pk>.*)/$',
        views.edit_productGroup, name='edit_productGroup'),
    url(r'^delete/productGroup/(?P<pk>.*)/$',
        views.delete_productGroup, name='delete_productGroup'),
    url(r'^search-productGroups/$', views.search_productGroups,
        name='search_productGroups'),
]
