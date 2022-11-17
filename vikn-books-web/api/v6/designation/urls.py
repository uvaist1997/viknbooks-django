from django.conf.urls import url, include
from api.v6.designation import views


urlpatterns = [
    url(r'^create-designation/$', views.create_designation,
        name='create_designation'),
    url(r'^designations/$', views.designations, name='designations'),
    url(r'^view/designation/(?P<pk>.*)/$',
        views.designation, name='designation'),
    url(r'^edit/designation/(?P<pk>.*)/$',
        views.edit_designation, name='edit_designation'),
    url(r'^delete/designation/(?P<pk>.*)/$',
        views.delete_designation, name='delete_designation'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
