from django.conf.urls import url, include
from api.v5.productCategories import views


urlpatterns = [
    url(r'^create-productCategory/$', views.create_productCategory,
        name='create_productCategory'),
    url(r'^productCategories/$', views.productCategories, name='productCategories'),
    url(r'^view/productCategory/(?P<pk>.*)/$',
        views.productCategory, name='productCategory'),
    url(r'^edit/productCategory/(?P<pk>.*)/$',
        views.edit_productCategory, name='edit_productCategory'),
    url(r'^delete/productCategory/(?P<pk>.*)/$',
        views.delete_productCategory, name='delete_productCategory'),
    url(r'^search-productCategories/$', views.search_productCategories,
        name='search_productCategories'),
]
