from django.conf.urls import url, include
from api.v5.leaveRequest import views


urlpatterns = [
    url(r'^create-leaveRequest/$', views.create_leaveRequest,
        name='create_leaveRequest'),
    url(r'^leaveRequests/$', views.leaveRequests, name='leaveRequests'),
    url(r'^view/leaveRequest/(?P<pk>.*)/$',
        views.leaveRequest, name='leaveRequest'),
    url(r'^edit/leaveRequest/(?P<pk>.*)/$',
        views.edit_leaveRequest, name='edit_leaveRequest'),
    url(r'^delete/leaveRequest/(?P<pk>.*)/$',
        views.delete_leaveRequest, name='delete_leaveRequest'),

    url(r'^leaveApprovals/$', views.leaveApprovals, name='leaveApprovals'),
    url(r'^approve/leaveRequest/(?P<pk>.*)/$',
        views.approve_leaveRequest, name='approve_leaveRequest'),
]
