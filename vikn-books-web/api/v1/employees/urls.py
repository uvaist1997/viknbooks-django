from django.conf.urls import url,include
from api.v1.employees import views

# app_name='companySettings'

urlpatterns = [
	url(r'^create-employee/$', views.create_employee, name='create_employee'),
    url(r'^employees/$', views.employees, name='employees'),
    url(r'^view/employee/(?P<pk>.*)/$', views.employee, name='employee'),
    url(r'^edit/employee/(?P<pk>.*)/$', views.edit_employee, name='edit_employee'),
    url(r'^delete/employee/(?P<pk>.*)/$', views.delete_employee, name='delete_employee'),

    url(r'^countries/$', views.countries, name='countries'),
]