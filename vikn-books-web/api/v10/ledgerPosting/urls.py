from django.conf.urls import url, include
from api.v10.ledgerPosting import views


urlpatterns = [
    url(r'^create-ledgerPosting/$', views.create_ledgerPosting,
        name='create_ledgerPosting'),
    url(r'^ledgerPostings/$', views.ledgerPostings, name='ledgerPostings'),
    url(r'^view/ledgerPosting/(?P<pk>.*)/$',
        views.ledgerPosting, name='ledgerPosting'),
    url(r'^edit/ledgerPosting/(?P<pk>.*)/$',
        views.edit_ledgerPosting, name='edit_ledgerPosting'),
    url(r'^delete/ledgerPosting/(?P<pk>.*)/$',
        views.delete_ledgerPosting, name='delete_ledgerPosting'),

    url(r'^query-trialBalance/$', views.query_trialBalance, name='query_trialBalance'),
    url(r'^trialBalance/$', views.trialBalance, name='trialBalance'),
    url(r'^ledgerReport/$', views.ledgerReport, name='ledgerReport'),
    url(r'^profit-and-loss/$', views.profitAndLoss, name='profitAndLoss'),
    url(r'^balance-Sheet/$', views.balanceSheet, name='balanceSheet'),

    url(r'^profit-and-loss-web/$', views.profitAndLoss_web, name='profitAndLoss_web'),
    url(r'^balance-sheet-web/$', views.balanceSheet_web, name='balanceSheet_web'),
    url(r'^balancing-sheet/$', views.balancing_sheet, name='balancing_sheet'),

    url(r'^day-book/$', views.DayBook, name='DayBook'),

    url(r'^trialBalance-webView/(?P<pk>.*)/$',
        views.trialBalance_webView, name='trialBalance_webView'),
    url(r'^ledgerReport-webView/(?P<pk>.*)/$',
        views.ledgerReport_webView, name='ledgerReport_webView'),

    url(r'^report/stock/$', views.report_stock, name='report_stock'),
    url(r'^report/stock-value/$', views.report_stockValue, name='report_stockValue'),
    url(r'^report/stock-value-singleProduct/$',
        views.report_stockValue_SingleProduct, name='report_stockValue_SingleProduct'),

    url(r'^cash-book/$', views.cash_book, name='cash_book'),
    url(r'^bank-book/$', views.bank_book, name='bank_book'),
    url(r'^outstanding-report/$', views.outstanding_report,
        name='outstanding_report'),

    url(r'^ledgerReport-excel/$', views.ledgerReport_excel,
        name='ledgerReport_excel'),
    url(r'^trialBalance-excel/$', views.trialBalance_excel,
        name='trialBalance_excel'),
    url(r'^profit-and-loss-excel/$',
        views.profitAndLoss_excel, name='profitAndLoss_excel'),
    url(r'^balance-Sheet-excel/$', views.balanceSheet_excel,
        name='balanceSheet_excel'),
    url(r'^day-book-excel/$', views.DayBook_excel, name='DayBook_excel'),
    url(r'^outstanding-report-excel/$', views.outStandingReport_excel,
        name='outStandingReport_excel'),

]
