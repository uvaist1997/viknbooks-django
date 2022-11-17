from django.conf.urls import url, include
from api.v10.workingTime import views

urlpatterns = [
    url(r'^create-working-time/$', views.create_working_time,
        name='create_working_time'),
    url(r'^edit-working_time/(?P<pk>.*)/$',
        views.edit_working_time, name='edit_working_time'),
    url(r'^working-times/$', views.working_times, name='working_times'),
    url(r'^working-time/(?P<pk>.*)/$', views.working_time, name='working_time'),
    url(r'^delete-working-time/(?P<pk>.*)/$',
        views.delete_working_time, name='delete_working_time'),
]
