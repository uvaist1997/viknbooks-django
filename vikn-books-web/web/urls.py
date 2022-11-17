from django.conf.urls import  url,include
from web import views


app_name = "web"

urlpatterns = [

    url(r'^$',views.home, name="home"),
    # url(r'create-brand/',views.create_brand, name="create_brand"),
    # url(r'brands/',views.brands, name="brands"),
    # url(r'^edit-brand/(?P<pk>.*)/$', views.edit_brand, name='edit_brand'),
    # url(r'^delete-brand/(?P<pk>.*)/$', views.delete_brand, name='delete_brand'),

    # url(r'account-groups/',views.account_groups, name="account_groups"),

    # url(r'create-branch/',views.create_branch, name="create_branch"),
    # url(r'branchs/',views.branchs, name="branchs"),
    # url(r'^edit-branch/(?P<pk>.*)/$', views.edit_branch, name='edit_branch'),
    # url(r'^delete-branch/(?P<pk>.*)/$', views.delete_branch, name='delete_branch'),

    # url(r'create-accountLedger/',views.create_accountLedger, name="create_accountLedger"),
    # url(r'accountLedgers/',views.accountLedgers, name="accountLedgers"),
    # url(r'^edit-accountLedger/(?P<pk>.*)/$', views.edit_accountLedger, name='edit_accountLedger'),
    # url(r'^delete-accountLedger/(?P<pk>.*)/$', views.delete_accountLedger, name='delete_accountLedger'),

    # url(r'create-bank/',views.create_bank, name="create_bank"),
    # url(r'banks/',views.banks, name="banks"),
    # url(r'^edit-bank/(?P<pk>.*)/$', views.edit_bank, name='edit_bank'),

]