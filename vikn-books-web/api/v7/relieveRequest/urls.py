from django.conf.urls import url, include
from api.v7.relieveRequest import views


urlpatterns = [
    url(r'^create-relieveRequest/$', views.create_relieveRequest,
        name='create_relieveRequest'),
    url(r'^relieveRequests/$', views.relieveRequests, name='relieveRequests'),
    url(r'^view/relieveRequest/(?P<pk>.*)/$',
        views.relieveRequest, name='relieveRequest'),
    url(r'^edit/relieveRequest/(?P<pk>.*)/$',
        views.edit_relieveRequest, name='edit_relieveRequest'),
    url(r'^delete/relieveRequest/(?P<pk>.*)/$',
        views.delete_relieveRequest, name='delete_relieveRequest'),

    url(r'^relieveApprovals/$', views.relieveApprovals, name='relieveApprovals'),
    url(r'^approve/relieveRequest/(?P<pk>.*)/$',
        views.approve_relieveRequest, name='approve_relieveRequest'),

]
