from django.conf.urls import  url,include
from django.urls import path
# from main import views as general_views
from users import views
app_name = 'users'

urlpatterns = [
    # url(r'^$', views.dashboard, name='dashboard'),
    # url(r'^$', views.companies, name='companies'),
    url(r'^create-db-user/(?P<pk>.*)/$',views.create_db_user,name="create_db_user"), 
    url(r'^login-db-user/$',views.login_db_user,name="login_db_user"),
    url(r'^create-user',views.create_user,name="create_user"),
    # url(r'^create-database/(?P<pk>.*)/$',views.create_database,name="create_database"),
    # path("create-user", views.create_user, name="Create User"),
]