from django.conf.urls import url, include
from api.v6.attendance import views


urlpatterns = [
    url(r'^create-attendance/$', views.create_attendance,
        name='create_attendance'),
    url(r'^attendances/$', views.attendances, name='attendances'),
    url(r'^view/attendance/(?P<pk>.*)/$',
        views.attendance, name='attendance'),
    url(r'^edit/attendance/(?P<pk>.*)/$',
        views.edit_attendance, name='edit_attendance'),
    url(r'^delete/attendance/(?P<pk>.*)/$',
        views.delete_attendance, name='delete_attendance'),

]
