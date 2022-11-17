from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.views.decorators.http import require_GET
from django.core import serializers
from django.contrib.auth.models import Group
from django.db.models import Sum, Q
import datetime
from rest_framework.decorators import api_view, permission_classes, renderer_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from main.functions import get_company
from rest_framework.response import Response
from rest_framework import status
from brands import models as table
from django.contrib.auth.models import User
from main import serializers as serializer
from main import functions as function


@login_required
def app(request):
    return HttpResponseRedirect(reverse('dashboard'))


@login_required
@require_GET
def color_scheme(request):
    color_scheme = request.GET.get('color-scheme-mode')
    print(color_scheme)
    print("hellooooooooooooooooooooooooooooooooooooooo")
    if color_scheme:
        ThemeSettings.objects.color_scheme.create(
            color_scheme=color_scheme
        )
        response_data = {}
        response_data['status'] = 'true'
        response_data['title'] = "Success"
        response_data['message'] = 'Theme switched successfully.'
    else:
        response_data = {}
        response_data['status'] = 'false'
        response_data['title'] = "Something Wrong!!!"
        response_data['stable'] = "true"
        response_data['message'] = 'Sorry Try again later.'

    return HttpResponse(json.dumps(response_data), content_type='application/javascript')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def generateVoucherNo(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    VoucherType = data['VoucherType']
    BranchID = data['BranchID']

    old_invoiceNo = 0
    PreFix = VoucherType
    seperator = ""
    model = function.get_model(VoucherType)
    if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID, VoucherType=VoucherType, LastInvoiceNo__isnull=False).exists():
        # instances = table.VoucherNoGenerateTable.objects.filter(
        #     CompanyID=CompanyID, VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True)
        voucher = table.VoucherNoGenerateTable.objects.filter(
            CompanyID=CompanyID, VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).first()
        old_invoiceNo = voucher.LastInvoiceNo
        PreFix = voucher.PreFix
        seperator = voucher.Seperater

 
        new_invoiceNo = int(old_invoiceNo) + 1
        if VoucherType == "PT" or VoucherType == "RT":
            new_invoiceNo = "{:04d}".format(new_invoiceNo)

        new_VoucherNo = PreFix + seperator + str(new_invoiceNo)
    else:
        new_VoucherNo, new_invoiceNo, PreFix, seperator = function.get_voucher(
            model, CompanyID, BranchID, UserID, VoucherType)
    # user_count = table.UserTable.objects.filter(CompanyID=CompanyID).count()
    # if user_count == 1:
    #     if table.VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).exists():
    #         voucher = table.VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).first()
    #         old_invoiceNo =  voucher.LastInvoiceNo
    #         PreFix = voucher.PreFix
    #         seperator = voucher.Seperater
    # else:
    #     user_name = User.objects.get(id=UserID).username
    #     PreFix = user_name[0:3]
    #     if table.VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).exists():
    #         voucher = table.VoucherNoTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exclude(LastInvoiceNo__isnull=True).first()
    #         old_invoiceNo =  voucher.LastInvoiceNo
    #         PreFix = voucher.PreFix
    #         seperator = voucher.Seperater

    response_data = {
        "StatusCode": 6000,
        "VoucherNo": new_VoucherNo,
        "InvoiceNo": new_invoiceNo,
        "PreFix": PreFix,
        "Seperator": seperator,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def formset_values(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    BranchID = data['BranchID']
    VoucherType = data['VoucherType']
    SettingsName = data['SettingsName']
    SettingsValue = data['SettingsValue']
    Type = data['Type']

    datas = []
    StatusCode = 6001

    if Type == "changes":
        if table.FormsetSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, SettingsName=SettingsName).exists():
            formset_datas = table.FormsetSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
            data = formset_datas.filter(SettingsName=SettingsName).first()
            data.SettingsValue = SettingsValue
            data.save()
        else:
            table.FormsetSettings.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                VoucherType=VoucherType,
                SettingsName=SettingsName,
                SettingsValue=SettingsValue,
            )
        StatusCode = 6000
    elif Type == "default":
        default_values = [{
                "SettingsName": "is_product_code",
                "SettingsValue": False
            },{
                "SettingsName": "is_barcode",
                "SettingsValue": False
            },{
                "SettingsName": "is_name",
                "SettingsValue": True
            },{
                "SettingsName": "is_description",
                "SettingsValue": False
            },{
                "SettingsName": "is_unit",
                "SettingsValue": True
            },{
                "SettingsName": "is_qty",
                "SettingsValue": True
            },{
                "SettingsName": "is_free_qty",
                "SettingsValue": False
            },{
                "SettingsName": "is_rate",
                "SettingsValue": True
            },{
                "SettingsName": "is_inclusive_tax",
                "SettingsValue": False
            },{
                "SettingsName": "is_gross_amount",
                "SettingsValue": True
            },{
                "SettingsName": "is_discount_percentage",
                "SettingsValue": False
            },{
                "SettingsName": "is_discount_amount",
                "SettingsValue": False
            },{
                "SettingsName": "is_tax",
                "SettingsValue": True
            },{
                "SettingsName": "is_amount",
                "SettingsValue": True
            },{
                "SettingsName": "is_bachcode",
                "SettingsValue": False
            },{
                "SettingsName": "is_mfg_date",
                "SettingsValue": True
            },{
                "SettingsName": "is_exp_date",
                "SettingsValue": True
            },
        ]
        for i in default_values:
            if table.FormsetSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, SettingsName=i['SettingsName']).exists():
                formset_datas = table.FormsetSettings.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
                data = formset_datas.filter(SettingsName=i['SettingsName']).first()
                data.SettingsValue = i['SettingsValue']
                data.save()
            else:
                table.FormsetSettings.objects.create(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    SettingsName=i['SettingsName'],
                    SettingsValue=i['SettingsValue'],
                )
            StatusCode = 6000
    else:
        if table.FormsetSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():
            formset_datas = table.FormsetSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
            serialized = serializer.FormsetSettingsSerializer(
                formset_datas, many=True)
            datas = serialized.data
            StatusCode = 6000

    response_data = {
        "StatusCode": StatusCode,
        "datas": datas
    }

    return Response(response_data, status=status.HTTP_200_OK)
