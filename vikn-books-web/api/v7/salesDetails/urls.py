from django.conf.urls import url, include
from api.v7.salesDetails import views


urlpatterns = [
    url(r'^create-salesDetails/$', views.create_salesDetails,
        name='create_salesDetails'),
    url(r'^list/salesDetails/$', views.list_salesDetails, name='list_salesDetails'),
    url(r'^view/salesDetail/(?P<pk>.*)/$',
        views.salesDetail, name='salesDetail'),
    url(r'^edit/salesDetails/(?P<pk>.*)/$',
        views.edit_salesDetails, name='edit_salesDetails'),
    url(r'^delete/salesDetails/(?P<pk>.*)/$',
        views.delete_salesDetails, name='delete_salesDetails'),

    url(r'^create-salesDetailsDummy/$', views.create_salesDetailsDummy,
        name='create_salesDetailsDummy'),
    url(r'^list/salesDetailsDummy/$', views.list_salesDetailsDummy,
        name='list_salesDetailsDummy'),
    url(r'^edit/salesDetailsDummy/(?P<pk>.*)/$',
        views.edit_salesDetailsDummy, name='edit_salesDetailsDummy'),
    url(r'^delete/salesDetailsDummy/(?P<pk>.*)/$',
        views.delete_salesDetailsDummy, name='delete_salesDetailsDummy'),

    url(r'^create-DummyforEditMaster/$', views.create_DummyforEditMaster,
        name='create_DummyforEditMaster'),

    url(r'^clear-Dummies/$', views.clear_dummies, name='clear_dummies'),
]
