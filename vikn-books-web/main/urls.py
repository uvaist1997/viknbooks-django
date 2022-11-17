from django.conf.urls import  url,include
from main import views

app_name = "main"
urlpatterns = [
    url(r'color_scheme/',views.color_scheme, name="color_scheme"),
    url(r'^generate/voucherNo/$', views.generateVoucherNo, name='generateVoucherNo'),
    url(r'^formset/values/$', views.formset_values, name='formset_values'),
]