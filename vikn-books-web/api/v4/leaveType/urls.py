from django.conf.urls import url, include
from api.v4.leaveType import views


urlpatterns = [
    url(r'^create-leaveType/$', views.create_leaveType,
        name='create_leaveType'),
    url(r'^leaveTypes/$', views.leaveTypes, name='leaveTypes'),
    url(r'^view/leaveType/(?P<pk>.*)/$',
        views.leaveType, name='leaveType'),
    url(r'^edit/leaveType/(?P<pk>.*)/$',
        views.edit_leaveType, name='edit_leaveType'),
    url(r'^delete/leaveType/(?P<pk>.*)/$',
        views.delete_leaveType, name='delete_leaveType'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
