from django.conf.urls import url, include
from api.v8.bankReconciliationStatement import views
app_name = "api.v8.bankReconciliationStatement"

urlpatterns = [
    # url(r'^create-brand/$', views.create_brand, name='create_brand'),
    url(r'^bank-payment-and-receipt/$', views.bank_payment_and_receipt,
        name='bank_payment_and_receipt'),
]
