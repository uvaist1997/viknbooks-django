from django.conf.urls import url, include
from api.v4.transactionTypes import views


urlpatterns = [
    url(r'^create-transactionType/$', views.create_transactionType,
        name='create_transactionType'),
    url(r'^transactionTypes/$', views.transactionTypes, name='transactionTypes'),
    url(r'^view/transactionType/(?P<pk>.*)/$',
        views.transactionType, name='transactionType'),
    url(r'^edit/transactionType/(?P<pk>.*)/$',
        views.edit_transactionType, name='edit_transactionType'),
    url(r'^delete/transactionType/(?P<pk>.*)/$',
        views.delete_transactionType, name='delete_transactionType'),

    url(r'^transactionTypesByMasterName/$',
        views.transactionTypesByMasterName, name='transactionTypesByMasterName'),
]
