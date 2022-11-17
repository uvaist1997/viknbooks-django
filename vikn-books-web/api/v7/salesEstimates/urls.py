from django.conf.urls import url, include
from api.v7.salesEstimates import views


urlpatterns = [
    url(r'^create-salesEstimate/$', views.create_salesEstimate,
        name='create_salesEstimate'),
    url(r'^edit/salesEstimate/(?P<pk>.*)/$',
        views.edit_salesEstimate, name='edit_salesEstimate'),
    url(r'^list/salesEstimateMaster/$', views.list_salesEstimateMaster,
        name='list_salesEstimateMaster'),
    url(r'^view/salesEstimateMaster/(?P<pk>.*)/$',
        views.salesEstimateMaster, name='salesEstimateMaster'),
    url(r'^delete/salesEstimateMaster/(?P<pk>.*)/$',
        views.delete_salesEstimateMaster, name='delete_salesEstimateMaster'),

    url(r'^salesEstimate-pagination/$', views.salesEstimate_pagination,
        name='salesEstimate_pagination'),
    url(r'^cancel/salesEstimateMaster/(?P<pk>.*)/$',
        views.cancel_salesEstimateMaster, name='cancel_salesEstimateMaster'),
]
