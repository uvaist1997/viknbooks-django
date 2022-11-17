from django.conf.urls import url, include
from api.v4.salesMaster import views


urlpatterns = [
    url(r'^create-salesMaster/$', views.create_salesMaster,
        name='create_salesMaster'),
    url(r'^list/salesMaster/$', views.list_salesMaster, name='list_salesMaster'),
    url(r'^view/salesMaster/(?P<pk>.*)/$',
        views.salesMaster, name='salesMaster'),
    url(r'^edit/salesMaster/(?P<pk>.*)/$',
        views.edit_salesMaster, name='edit_salesMaster'),
    url(r'^delete/salesMaster/(?P<pk>.*)/$',
        views.delete_salesMaster, name='delete_salesMaster'),
]
