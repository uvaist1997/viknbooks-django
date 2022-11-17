import base64
import codecs
import datetime
import json
import tempfile
from io import BytesIO, StringIO

import pdfkit
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from html2image import Html2Image
from num2words import num2words
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from pytz import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

# from brands.models import Settings, Settings_Log, PrintSettings, BarcodeSettings, Language
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from weasyprint import CSS, HTML

from api.v10.brands.serializers import ListSerializer
from api.v10.companySettings.serializers import CompanySettingsPrintRestSerializer
from api.v10.ledgerPosting.functions import (
    ledgerReport_excel_data,
    outStandingReport_excel_data,
    trialBalance_excel_data,
)
from api.v10.payments.functions import paymentReport_excel_data
from api.v10.payments.serializers import PaymentMasterRestSerializer
from api.v10.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
from api.v10.purchases.functions import purchase_excel_data, purchaseReturn_excel_data
from api.v10.purchases.serializers import (
    PurchaseMasterRestSerializer,
    PurchaseMasterSerializer,
)
from api.v10.receipts.functions import receiptReport_excel_data
from api.v10.sales.functions import (
    sales_excel_data,
    salesReturn_excel_data,
    taxSummary_excel_data,
)
from api.v10.sales.serializers import SalesMasterRestSerializer
from api.v10.salesReturns.serializers import SalesReturnMasterRestSerializer
from api.v10.settings import serializers
from api.v10.settings.functions import (
    convert_to_base64,
    create_or_update_user_type_settings,
    generate_serializer_errors,
    get_auto_id,
    get_client_ip,
    get_country_time,
    get_user_type_settings,
    html_to_pdf_pisa,
    render_to_pdf,
)
from brands import models
from main.functions import ConvertedTime, activity_log, get_company


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def print_paper(request):
    writer = PdfFileWriter()
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    no_of_copies = int(request.GET.get("no_of_copies"))
    invoice_type = request.GET.get("invoice_type")
    invoice_id = request.GET.get("invoice_id")
    try:
        PriceRounding = int(request.GET.get("PriceRounding"))
    except:
        PriceRounding = 2
    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    branch_instance = models.Branch.objects.get(
        BranchID=BranchID, CompanyID=company_instance
    )
    company_name = branch_instance.DisplayName
    country_instance = models.Country.objects.get(id=company_instance.Country.id)
    print_settings_instance, created = models.PrintSettingsNew.objects.get_or_create(
        CompanyID=company_instance, InvoiceType=invoice_type
    )

    data = {}
    grand_total = 0
    details = {}
    qr_code = None
    instance_serialized = {}
    invoice_time = ""
    if invoice_type == "sales_invoice":
        if models.SalesMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_invoice":
        if models.PurchaseMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "sales_return":
        if models.SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.SalesReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = SalesReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["SalesReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "purchase_return":
        if models.PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PurchaseReturnMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PurchaseReturnMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "request": request,
                },
            ).data
            details = instance_serialized["PurchaseReturnDetails"]
            grand_total = instance_serialized.get("GrandTotal_print")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    if invoice_type == "payment_voucher":
        if models.PaymentMaster.objects.filter(
            CompanyID=CompanyID, pk=invoice_id
        ).exists():
            instance = models.PaymentMaster.objects.get(
                CompanyID=CompanyID, pk=invoice_id
            )
            instance_serialized = PaymentMasterRestSerializer(
                instance,
                many=False,
                context={
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            ).data
            details = instance_serialized["PaymentDetails"]
            grand_total = instance_serialized.get("TotalAmount_rounded")
            invoice_time = get_country_time(
                instance.CreatedDate, country_instance.Country_Name
            )

    company_instance = models.CompanySettings.objects.get(id=CompanyID)
    serialized = CompanySettingsPrintRestSerializer(
        company_instance, many=False, context={"request": request}
    )
    data = {
        "company_name": company_name,
        "country": country_instance,
        "invoice_type": invoice_type,
        "type": "pdf",
        "company": serialized.data,
        "amount_in_words": num2words(grand_total, to="cardinal", lang="en_IN"),
        "details": details,
        "data": instance_serialized,
        "PriceRounding": PriceRounding,
        "settings": print_settings_instance,
        "qr_code": qr_code,
        "invoice_time": invoice_time,
    }
    if invoice_type == "payment_voucher":
        template = get_template("payment_print.html")
    else:
        if print_settings_instance.template == "template3":
            template = get_template("print_template_three.html")
        elif print_settings_instance.template == "template2":
            template = get_template("print_template_two.html")
        else:
            template = get_template("print.html")

    html = template.render(data)

    options = {
        "page-size": "Letter",
        "encoding": "UTF-8",
        "margin-top": "0.5in",
        "margin-right": "0.5in",
        "margin-bottom": "0.5in",
        "margin-left": "0.5in",
        "custom-header": [("Accept-Encoding", "gzip")],
    }
    for i in range(no_of_copies):
        stream = BytesIO()
        stream.write(pdfkit.from_string(html, False, options=options))
        count = PdfFileReader(stream).numPages
        # writer.addPage(PdfFileReader(stream).getPage(0))

        for j in range(count):
            page = PdfFileReader(stream).getPage(j)
            writer.addPage(page)
    output = BytesIO()
    pdf = writer.write(output)
    pdf = pdfkit.from_string(html, False, options)
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    # response = HttpResponse(pdf, content_type='application/pdf')
    response["Content-Disposition"] = "inline"
    response["X-Frame-Options"] = "allow-all"
    # response['content-security-policy'] = "frame-ancestors 'self' http://localhost:3000"
    return response
