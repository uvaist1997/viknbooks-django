from django.conf.urls import  url,include
from accounts import views


app_name = "accounts"

urlpatterns = [
    # Masters
    url(r'create-accountGroup/',views.create_accountGroup, name="create_accountGroup"),
    url(r'account-groups/',views.account_groups, name="account_groups"),
    url(r'^view-accountGroup/(?P<pk>.*)/$', views.view_accountGroup, name='view_accountGroup'),
    url(r'^edit-accountGroup/(?P<pk>.*)/$', views.edit_accountGroup, name='edit_accountGroup'),
    url(r'^delete-accountGroup/(?P<pk>.*)/$', views.delete_accountGroup, name='delete_accountGroup'),

    url(r'create-accountLedger/',views.create_accountLedger, name="create_accountLedger"),
    url(r'accountLedgers/',views.accountLedgers, name="accountLedgers"),
    url(r'^view-accountLedger/(?P<pk>.*)/$', views.view_accountLedger, name='view_accountLedger'),
    url(r'^edit-accountLedger/(?P<pk>.*)/$', views.edit_accountLedger, name='edit_accountLedger'),
    url(r'^delete-accountLedger/(?P<pk>.*)/$', views.delete_accountLedger, name='delete_accountLedger'),

    url(r'create-branch/',views.create_branch, name="create_branch"),
    url(r'branchs/',views.branchs, name="branchs"),
    url(r'^view-branch/(?P<pk>.*)/$', views.view_branch, name='view_branch'),
    url(r'^edit-branch/(?P<pk>.*)/$', views.edit_branch, name='edit_branch'),
    url(r'^delete-branch/(?P<pk>.*)/$', views.delete_branch, name='delete_branch'),

    url(r'create-bank/',views.create_bank, name="create_bank"),
    url(r'banks/',views.banks, name="banks"),
    url(r'^edit-bank/(?P<pk>.*)/$', views.edit_bank, name='edit_bank'),
    url(r'^view-bank/(?P<pk>.*)/$', views.view_bank, name='view_bank'),
    url(r'^delete-bank/(?P<pk>.*)/$', views.delete_bank, name='delete_bank'),

    url(r'create-customer/',views.create_customer, name="create_customer"),
    url(r'customers/',views.customers, name="customers"),
    url(r'^view-customer/(?P<pk>.*)/$', views.view_customer, name='view_customer'),
    url(r'^edit-customer/(?P<pk>.*)/$', views.edit_customer, name='edit_customer'),
    url(r'^delete-customer/(?P<pk>.*)/$', views.delete_customer, name='delete_customer'),


    url(r'create-supplier/',views.create_supplier, name="create_supplier"),
    url(r'suppliers/',views.suppliers, name="suppliers"),
    url(r'^view-supplier/(?P<pk>.*)/$', views.view_supplier, name='view_supplier'),
    url(r'^edit-supplier/(?P<pk>.*)/$', views.edit_supplier, name='edit_supplier'),
    url(r'^delete-supplier/(?P<pk>.*)/$', views.delete_supplier, name='delete_supplier'),

    url(r'create-transactionType/',views.create_transactionType, name="create_transactionType"),
    url(r'transactionTypes/',views.transactionTypes, name="transactionTypes"),
    url(r'^view-transactionType/(?P<pk>.*)/$', views.view_transactionType, name='view_transactionType'),
    url(r'^edit-transactionType/(?P<pk>.*)/$', views.edit_transactionType, name='edit_transactionType'),
    url(r'^delete-transactionType/(?P<pk>.*)/$', views.delete_transactionType, name='delete_transactionType'),
    # Reports
    url(r'^trialBalance-webView/$', views.trialBalance_webView, name='trialBalance_webView'),
    url(r'^ledgerReport-webView/$', views.ledgerReport_webView, name='ledgerReport_webView'),
    url(r'^ledgerReport-ledgerWise/$', views.ledgerReport_LedgerWise, name='ledgerReport_LedgerWise'),
    url(r'^profit-and-loss-webview/$', views.profitAndLoss_webView, name='profitAndLoss_webView'),

    url(r'create-cash-payment/',views.create_cash_payment, name="create_cash_payment"),
    url(r'cash-payments/',views.cash_payments, name="cash_payments"),
    url(r'^cash-payment/(?P<pk>.*)/$', views.cash_payment, name='cash_payment'),
    url(r'^edit-cash-payment/(?P<pk>.*)/$', views.edit_cash_payment, name='edit_cash_payment'),
    url(r'^delete-cash-payment/(?P<pk>.*)/$', views.delete_cash_payment, name='delete_cash_payment'),

    url(r'create-cash-receipt/',views.create_cash_receipt, name="create_cash_receipt"),
    url(r'cash-receipts/',views.cash_receipts, name="cash_receipts"),
    url(r'^cash-receipt/(?P<pk>.*)/$', views.cash_receipt, name='cash_receipt'),
    url(r'^edit-cash-receipt/(?P<pk>.*)/$', views.edit_cash_receipt, name='edit_cash_receipt'),
    url(r'^delete-cash-receipt/(?P<pk>.*)/$', views.delete_cash_receipt, name='delete_cash_receipt'),
    

    url(r'create-journal-entry/',views.create_journal_entry, name="create_journal_entry"),
    url(r'journal-entries/',views.journal_entries, name="journal_entries"),
    url(r'^journal-entry/(?P<pk>.*)/$', views.journal_entry, name='journal_entry'),
    url(r'^edit-journal-entry/(?P<pk>.*)/$', views.edit_journal_entry, name='edit_journal_entry'),
    url(r'^delete-journal-entry/(?P<pk>.*)/$', views.delete_journal_entry, name='delete_journal_entry'),

    url(r'create-bank-payment/',views.create_bank_payment, name="create_bank_payment"),
    url(r'bank-payments/',views.bank_payments, name="bank_payments"),
    url(r'^bank-payment/(?P<pk>.*)/$', views.bank_payment, name='bank_payment'),
    url(r'^edit-bank-payment/(?P<pk>.*)/$', views.edit_bank_payment, name='edit_bank_payment'),
    url(r'^delete-bank-payment/(?P<pk>.*)/$', views.delete_bank_payment, name='delete_bank_payment'),

    url(r'create-bank-receipt/',views.create_bank_receipt, name="create_bank_receipt"),
    url(r'bank-receipts/',views.bank_receipts, name="bank_receipts"),
    url(r'^bank-receipt/(?P<pk>.*)/$', views.bank_receipt, name='bank_receipt'),
    url(r'^edit-bank-receipt/(?P<pk>.*)/$', views.edit_bank_receipt, name='edit_bank_receipt'),
    url(r'^delete-bank-receipt/(?P<pk>.*)/$', views.delete_bank_receipt, name='delete_bank_receipt'),


]