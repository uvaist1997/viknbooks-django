from django.conf.urls import url, include
from api.v3.accountLedgers import views


urlpatterns = [
    url(r'^create-accountLedger/$', views.create_accountLedger,
        name='create_accountLedger'),
    url(r'^accountLedgers/$', views.accountLedgers, name='accountLedgers'),
    url(r'^view/accountLedger/(?P<pk>.*)/$',
        views.accountLedger, name='accountLedger'),
    url(r'^edit/accountLedger/(?P<pk>.*)/$',
        views.edit_accountLedger, name='edit_accountLedger'),
    url(r'^delete/accountLedger/(?P<pk>.*)/$',
        views.delete_accountLedger, name='delete_accountLedger'),

    url(r'^get-balance-ledger/$', views.get_balance_ledger,
        name='get_balance_ledger'),

    url(r'^ledgerListByID/$', views.ledgerListByID, name='ledgerListByID'),
    url(r'^ledgerListforPayments/$', views.ledgerListforPayments,
        name='ledgerListforPayments'),
    url(r'^ledgerListByGroupUnder/$', views.ledgerListByGroupUnder,
        name='ledgerListByGroupUnder'),
    # url(r'^generate/LedgerCode/$', views.generateLedgerCode, name='generateLedgerCode'),
    url(r'^ledgerListforPayments-Receipts/$',
        views.ledgerListforPayments_Receipts, name='ledgerListforPayments_Receipts'),

    url(r'^ledgerListByGroups/$', views.ledgerListByGroups,
        name='ledgerListByGroups'),
]
