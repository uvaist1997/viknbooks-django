from django.conf.urls import url, include
from api.v5.leave import views


urlpatterns = [
    url(r'^create-leave/$', views.create_leave,
        name='create_leave'),
    url(r'^leaves/$', views.leaves, name='leaves'),
    url(r'^view/leave/(?P<pk>.*)/$',
        views.leave, name='leave'),
    url(r'^edit/leave/(?P<pk>.*)/$',
        views.edit_leave, name='edit_leave'),
    url(r'^delete/leave/(?P<pk>.*)/$',
        views.delete_leave, name='delete_leave'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
