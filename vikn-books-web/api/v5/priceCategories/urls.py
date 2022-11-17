from django.conf.urls import url, include
from api.v5.priceCategories import views


urlpatterns = [
    url(r'^create-priceCategory/$', views.create_priceCategory,
        name='create_priceCategory'),
    url(r'^priceCategories/$', views.priceCategories, name='priceCategories'),
    url(r'^view/priceCategory/(?P<pk>.*)/$',
        views.priceCategory, name='priceCategory'),
    url(r'^edit/priceCategory/(?P<pk>.*)/$',
        views.edit_priceCategory, name='edit_priceCategory'),
    url(r'^delete/priceCategory/(?P<pk>.*)/$',
        views.delete_priceCategory, name='delete_priceCategory'),
]
