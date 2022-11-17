from django.conf.urls import url, include
from api.v7.expense import views


urlpatterns = [
    url(r'^create-expense/$', views.create_expense, name='create_expense'),
    url(r'^list-expense/$', views.list_expense, name='list_expense'),
    url(r'^view/expense/(?P<pk>.*)/$',views.expense, name='expense'),
    url(r'^edit/expense/(?P<pk>.*)/$',views.edit_expense, name='edit_expense'),
    url(r'^delete/expense/(?P<pk>.*)/$',
        views.delete_expense, name='delete_expense'),
]
