from django.conf.urls import url,include
# from api.v1.colors import views
from brands import views
app_name = 'reviews'


urlpatterns = [
	# url(r'^create-color/$', views.create_color, name='create_color'),
 #    url(r'^colors/$', views.colors, name='colors'),
 #    url(r'^view/color/(?P<pk>.*)/$', views.color, name='color'),
 #    url(r'^edit/color/(?P<pk>.*)/$', views.edit_color, name='edit_color'),
 #    url(r'^delete/color/(?P<pk>.*)/$', views.delete_color, name='delete_color'),

 #    url(r'^create-testImage/$', views.create_testImage, name='create_testImage'),


    # url(r'^$',views.user_signup,name="user_signup"),
    # url(r'^user-login/$',views.user_login,name="user_login"),
    # url(r'^create-db-user/(?P<pk>[0-9]+)/(?P<created_user_id>[0-9]+)$',views.create_db_user,name="create_db_user"), 
    # url(r'^create-company/$',views.create_company,name="create_company"), 
    
    # url(r'^$',views.create_companies,name="user_signup"),
    # url(r'^create-companies/(?P<pk>.*)/$',views.create_companies,name="create_companies"), 
    # (?# url(r'^login-db-user/$',views.login_db_user,name="login_db_user"),)
    # url(r'^dashboard/$',views.dashboard,name="dashboard"),

    # url(r'create-formsetTest/',views.create_formsetTest, name="create_formsetTest"),
    # url(r'formsetTests/',views.formsetTests, name="formsetTests"),
    # url(r'^edit-formsetTest/(?P<pk>.*)/$', views.edit_formsetTest, name='edit_formsetTest'),


]
