from django.conf.urls import url, include
from api.v3.purchaseMaster import views


urlpatterns = [
    url(r'^create-purchaseMaster/$', views.create_purchaseMaster,
        name='create_purchaseMaster'),
    url(r'^list/purchaseMaster/$', views.list_purchaseMaster,
        name='list_purchaseMaster'),
    url(r'^view/purchaseMaster/(?P<pk>.*)/$',
        views.purchaseMaster, name='purchaseMaster'),
    url(r'^edit/purchaseMaster/(?P<pk>.*)/$',
        views.edit_purchaseMaster, name='edit_purchaseMaster'),
    url(r'^delete/purchaseMaster/(?P<pk>.*)/$',
        views.delete_purchaseMaster, name='delete_purchaseMaster'),
]
