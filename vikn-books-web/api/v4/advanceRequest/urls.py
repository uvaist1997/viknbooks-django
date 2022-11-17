from django.conf.urls import url, include
from api.v4.advanceRequest import views


urlpatterns = [
    url(r'^create-advanceRequest/$', views.create_advanceRequest,
        name='create_advanceRequest'),
    url(r'^advanceRequests/$', views.advanceRequests, name='advanceRequests'),
    url(r'^view/advanceRequest/(?P<pk>.*)/$',
        views.advanceRequest, name='advanceRequest'),
    url(r'^edit/advanceRequest/(?P<pk>.*)/$',
        views.edit_advanceRequest, name='edit_advanceRequest'),
    url(r'^delete/advanceRequest/(?P<pk>.*)/$',
        views.delete_advanceRequest, name='delete_advanceRequest'),


    url(r'^advanceApprovals/$', views.advanceApprovals, name='advanceApprovals'),
    url(r'^approve/advanceRequest/(?P<pk>.*)/$',
        views.approve_advanceRequest, name='approve_advanceRequest'),
]
