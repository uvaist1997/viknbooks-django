from django.conf.urls import url, include
from api.v7.salaryComponent import views


urlpatterns = [
    url(r'^create-salaryComponent/$', views.create_salaryComponent,
        name='create_salaryComponent'),
    url(r'^salaryComponents/$', views.salaryComponents, name='salaryComponents'),
    url(r'^view/salaryComponent/(?P<pk>.*)/$',
        views.salaryComponent, name='salaryComponent'),
    url(r'^edit/salaryComponent/(?P<pk>.*)/$',
        views.edit_salaryComponent, name='edit_salaryComponent'),
    url(r'^delete/salaryComponent/(?P<pk>.*)/$',
        views.delete_salaryComponent, name='delete_salaryComponent'),

    # url(r'^create-department/$', views.create_department, name='create_department'),
    # url(r'^departments/$', views.departments, name='departments'),
    # url(r'^view/department/(?P<pk>.*)/$', views.department, name='department'),
    # url(r'^edit/department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    # url(r'^delete/department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
]
