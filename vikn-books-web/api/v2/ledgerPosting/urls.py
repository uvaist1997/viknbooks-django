from django.conf.urls import url,include
from api.v2.ledgerPosting import views


urlpatterns = [
	url(r'^create-ledgerPosting/$', views.create_ledgerPosting, name='create_ledgerPosting'),
    url(r'^ledgerPostings/$', views.ledgerPostings, name='ledgerPostings'),
    url(r'^view/ledgerPosting/(?P<pk>.*)/$', views.ledgerPosting, name='ledgerPosting'),
    url(r'^edit/ledgerPosting/(?P<pk>.*)/$', views.edit_ledgerPosting, name='edit_ledgerPosting'),
    url(r'^delete/ledgerPosting/(?P<pk>.*)/$', views.delete_ledgerPosting, name='delete_ledgerPosting'),

    url(r'^trialBalance/$', views.trialBalance, name='trialBalance'),
    url(r'^ledgerReport/$', views.ledgerReport, name='ledgerReport'),
    url(r'^profit-and-loss/$', views.profitAndLoss, name='profitAndLoss'),
    url(r'^balance-Sheet/$', views.balanceSheet, name='balanceSheet'),

    url(r'^profit-and-loss-web/$', views.profitAndLoss_web, name='profitAndLoss_web'),
    url(r'^balance-sheet-web/$', views.balanceSheet_web, name='balanceSheet_web'),
    url(r'^day-book/$', views.DayBook, name='DayBook'),

    url(r'^trialBalance-webView/(?P<pk>.*)/$', views.trialBalance_webView, name='trialBalance_webView'),
    url(r'^ledgerReport-webView/(?P<pk>.*)/$', views.ledgerReport_webView, name='ledgerReport_webView'),

    url(r'^report/stock/$', views.report_stock, name='report_stock'),
    url(r'^report/stock-value/$', views.report_stockValue, name='report_stockValue'),
    url(r'^report/stock-value-singleProduct/$', views.report_stockValue_SingleProduct, name='report_stockValue_SingleProduct'),

    url(r'^cash-book/$', views.cash_book, name='cash_book'),

]