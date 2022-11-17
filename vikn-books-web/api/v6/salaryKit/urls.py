from django.conf.urls import url, include
from api.v6.salaryKit import views


urlpatterns = [
    url(r'^create-salaryKit/$', views.create_salaryKit,
        name='create_salaryKit'),
    url(r'^salaryKits/$', views.salaryKits, name='salaryKits'),
    url(r'^view/salaryKit/(?P<pk>.*)/$',
        views.salaryKit, name='salaryKit'),
    url(r'^edit/salaryKit/(?P<pk>.*)/$',
        views.edit_salaryKit, name='edit_salaryKit'),
    url(r'^delete/salaryKit/(?P<pk>.*)/$',
        views.delete_salaryKit, name='delete_salaryKit'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
