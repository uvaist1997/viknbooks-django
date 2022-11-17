from django.conf.urls import url, include
from api.v8.department import views


urlpatterns = [
    url(r'^create-department/$', views.create_department, name='create_department'),
    url(r'^departments/$', views.departments, name='departments'),
    url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    url(r'^edit/department/(?P<pk>.*)/$',
        views.edit_department, name='edit_department'),
    url(r'^delete/department/(?P<pk>.*)/$',
        views.delete_department, name='delete_department'),
]
