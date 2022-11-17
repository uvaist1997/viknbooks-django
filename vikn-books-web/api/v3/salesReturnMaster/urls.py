from django.conf.urls import url, include
from api.v3.salesReturnMaster import views


urlpatterns = [
    url(r'^create-salesReturnMaster/$', views.create_salesReturnMaster,
        name='create_salesReturnMaster'),
    url(r'^list/salesReturnMaster/$', views.list_salesReturnMaster,
        name='list_salesReturnMaster'),
    url(r'^view/salesReturnMaster/(?P<pk>.*)/$',
        views.salesReturnMaster, name='salesReturnMaster'),
    url(r'^edit/salesReturnMaster/(?P<pk>.*)/$',
        views.edit_salesReturnMaster, name='edit_salesReturnMaster'),
    url(r'^delete/salesReturnMaster/(?P<pk>.*)/$',
        views.delete_salesReturnMaster, name='delete_salesReturnMaster'),
]
