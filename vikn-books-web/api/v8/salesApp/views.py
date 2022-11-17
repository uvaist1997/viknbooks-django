from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.salesApp.serializers import POS_ProductList_Serializer
from api.v8.brands.serializers import ListSerializer
from api.v8.salesApp.functions import generate_serializer_errors,get_pin_no,get_TokenNo,get_KitchenID
from rest_framework import status
import datetime
from main.functions import get_company,activity_log
from random import randint
from django.db import transaction,IntegrityError
from main.functions import update_voucher_table
import re,sys, os
from api.v8.accountLedgers.functions import get_auto_LedgerPostid
from api.v8.products.functions import get_auto_AutoBatchCode,update_stock
from api.v8.ledgerPosting.functions import convertOrderdDict
from api.v8.users.serializers import MyCompaniesSerializer, CompaniesSerializer
from brands import models as table
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date
from api.v8.parties.serializers import  PartiesRestSerializer, PartyListSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q, Prefetch, Sum
from api.v8.users.serializers import LoginSerializer
from api.v8.general.functions import get_current_role
from api.v8.posholds.serializers import POS_Product_Serializer


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_companies(request):
    userId = request.data['userId']
    userId = get_object_or_404(User.objects.filter(id=userId))
    my_company_instances = table.CompanySettings.objects.filter(
        owner=userId, is_deleted=False).exclude(business_type__Name="Restaurant")
    my_company_serialized = MyCompaniesSerializer(
        my_company_instances, many=True)
    my_company_json = convertOrderdDict(my_company_serialized.data)

    member_company_instances = table.UserTable.objects.filter(
        customer__user=userId).exclude(CompanyID__business_type__Name="Restaurant")
    member_company_serialized = CompaniesSerializer(
        member_company_instances, many=True)
    member_company_json = convertOrderdDict(member_company_serialized.data)

    data = []
    for i in my_company_json:
        id = i['id']
        CompanyImage = ""
        if my_company_instances.get(id=id).CompanyLogo:
            CompanyImage =  my_company_instances.get(id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        ExpiryDate = i['ExpiryDate']
        Permission = i['Permission']
        Edition = i['Edition']
        IsPosUser = i['IsPosUser']
        StateName = i['StateName']
        Email = i['Email']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'Edition': Edition,
            'IsPosUser': IsPosUser,
            'StateName': StateName,
            'Email': Email,
            'CompanyImage':CompanyImage
        }
        data.append(dic)

    for i in member_company_json:
        id = i['id']
        CompanyImage = ""
        if table.CompanySettings.objects.get(id=id).CompanyLogo:
            CompanyImage =  table.CompanySettings.objects.get(id=id).CompanyLogo.url
        CompanyName = i['CompanyName']
        company_type = i['company_type']
        Permission = i['Permission']
        Edition = i['Edition']
        IsPosUser = i['IsPosUser']
        StateName = i['StateName']
        Email = i['Email']
        ExpiryDate = date.today().strftime("%Y-%m-%d")
        if i['ExpiryDate'] != None:
            ExpiryDate = i['ExpiryDate']
        dic = {
            'id': id,
            'CompanyName': CompanyName,
            'company_type': company_type,
            'ExpiryDate': ExpiryDate,
            'Permission': Permission,
            'Edition': Edition,
            'IsPosUser': IsPosUser,
            'StateName': StateName,
            'Email': Email,
            'CompanyImage':CompanyImage
        }
        data.append(dic)

    tes_arry = []
    final_array = []
    for i in data:
        if not i['id'] in tes_arry:
            tes_arry.append(i['id'])
            final_array.append(i)

    CurrentVersion = 0
    MinimumVersion = 0
    if table.SoftwareVersion.objects.exists():
        CurrentVersion = table.SoftwareVersion.objects.get().CurrentVersion
        MinimumVersion = table.SoftwareVersion.objects.get().MinimumVersion

    software_version_dic = {
        "CurrentVersion": CurrentVersion,
        "MinimumVersion": MinimumVersion,
    }
    response_data = {
        "StatusCode": 6000,
        "data": final_array,
        "SoftwareVersion": software_version_dic
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_product_list(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    page_number = data['page_no']
    items_per_page = data['items_per_page']


    if table.Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        instances = table.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
        if page_number and items_per_page:
            instances = list_pagination(
                instances,
                items_per_page,
                page_number
            )
        
        serialized = POS_Product_Serializer(instances,many=True,context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_product_search(request):
    today = datetime.datetime.now()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']


    if table.Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        if length < 3:
            instances = table.Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                Q(ProductCode__icontains=product_name)))[:10]
        else:
            instances = table.Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                Q(ProductCode__icontains=product_name)))
        
        serialized = POS_Product_Serializer(instances,many=True,context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data" : serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No data",
        }

        return Response(response_data, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def pos_parties(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = PartyListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        PartyType = serialized1.data['PartyType']

        if PartyType == "1":
            PartyType = "customer"

        elif PartyType == "2":
            PartyType = "supplier"

        if PartyType == "0":

            if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if page_number and items_per_page:
                    instances = table.Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(instances)
                    ledger_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
                else:
                    ledger_sort_pagination = table.Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(ledger_sort_pagination)
                serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "count": count,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
                response_data = {
                    "StatusCode": 6001,
                    "message": "Parties not found in this branch."
                }

                return Response(response_data, status=status.HTTP_200_OK)

        elif table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType).exists():

            if page_number and items_per_page:
                instances = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(ledger_sort_pagination)

            serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                               "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
            response_data = {
                "StatusCode": 6001,
                "message": "Parties not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not Valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesApp_login(request):
    serialized = LoginSerializer(data=request.data)
    CreatedUserID = ""
    is_verified = False
    customer_ins = None
    data = request.data

    try:
        is_mobile = data['is_mobile']
    except:
        is_mobile = False

    if serialized.is_valid():
        username = serialized.data['username']
        password = serialized.data['password']

        if User.objects.filter(email=username).exists():
            email = username
            username = User.objects.get(email=email).username

        if User.objects.filter(username=username).exists():
            user_ins = User.objects.get(username=username)
            if user_ins.is_active == True:
                is_verified = True

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['current_role'] = get_current_role(request)
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"username": "' + username + \
                '", "password": "' + password + '" }'
            protocol = "http://"
            if request.is_secure():
                protocol = "https://"

            web_host = request.get_host()
            request_url = protocol + web_host + "/api/v1/auth/token/"
            response = requests.post(request_url, headers=headers, data=data)
            if response.status_code == 200:
                token_datas = response.json()
                LastToken = token_datas['access']

                if table.Customer.objects.filter(user__username=username).exists():
                    customer_ins = table.Customer.objects.filter(
                        user__username=username).first()
                    if is_mobile == True:
                        customer_ins.LastLoginTokenMobile = LastToken
                    else:
                        customer_ins.LastLoginToken = LastToken
                    customer_ins.save()

                data = response.json()
                success = 6000
                message = "Login successfully"

                return Response(
                    {
                        'success': success,
                        'data': data,
                        'refresh': data['refresh'],
                        'access': data['access'],
                        'user_id': data['user_id'],
                        'role': data['role'],
                        'message': message,
                        'error': None,
                        "CreatedUserID": CreatedUserID,
                        'username': username,
                    },
                    status=status.HTTP_200_OK)
            else:
                success = 6001
                data = None
                error = "please contact admin to solve this problem."
                return Response(
                    {
                        'success': success,
                        'data': data,
                        'error': error
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            success = 6001
            data = None
            if is_verified == False:
                error = "Please Verify Your Email to Login"
            else:
                error = "User not found"
            return Response(
                {
                    'success': success,
                    'data': data,
                    'error': error
                },
                status=status.HTTP_400_BAD_REQUEST)
    else:
        message = generate_serializer_errors(serialized._errors)
        success = 6001
        data = None
        return Response(
            {
                'success': success,
                'data': data,
                'error': message,
            },
            status=status.HTTP_400_BAD_REQUEST)