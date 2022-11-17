from django.conf.urls import  url,include
from payrolls import views


app_name = "payrolls"

urlpatterns = [
    url(r'create-designation/',views.create_designation, name="create_designation"),
    url(r'designations/',views.designations, name="designations"),
    url(r'^view/designation/(?P<pk>.*)/$', views.view_designation, name='view_designation'),
    url(r'^edit-designation/(?P<pk>.*)/$', views.edit_designation, name='edit_designation'),
    url(r'^delete-designation/(?P<pk>.*)/$', views.delete_designation, name='delete_designation'),

    url(r'create-department/',views.create_department, name="create_department"),
    url(r'departments/',views.departments, name="departments"),
    url(r'^view/department/(?P<pk>.*)/$', views.view_department, name='view_department'),
    url(r'^edit-department/(?P<pk>.*)/$', views.edit_department, name='edit_department'),
    url(r'^delete-department/(?P<pk>.*)/$', views.delete_department, name='delete_department'),
    
    url(r'create-employee/',views.create_employee, name="create_employee"),
    url(r'employees/',views.employees, name="employees"),
    url(r'^view/employee/(?P<pk>.*)/$', views.view_employee, name='view_employee'),
    url(r'^edit-employee/(?P<pk>.*)/$', views.edit_employee, name='edit_employee'),
    url(r'^delete-employee/(?P<pk>.*)/$', views.delete_employee, name='delete_employee'),
]