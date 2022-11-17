from api.v4.brands.tasks import create_random_user_accounts
from django.contrib.auth.models import User
from brands.models import Brand, Brand_Log, Product, Activity_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.brands.serializers import BrandSerializer, BrandRestSerializer, ListSerializer
from api.v4.brands.functions import generate_serializer_errors
from rest_framework import status
from api.v4.brands.functions import get_auto_id
from main.functions import get_company, activity_log
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_brand(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        BrandName = serialized.data['BrandName']
        Notes = serialized.data['Notes']

        Action = 'A'
        BrandID = get_auto_id(Brand, BranchID, CompanyID)
        if not Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exists():

            Brand.objects.create(
                BrandID=BrandID,
                BranchID=BranchID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Create', 'Brand created successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Brand', 'Create', 'Brand name already exist.', 'same name exists.')

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Brand', 'Create',
                     'Brand field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    instance = Brand.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    BrandID = instance.BrandID
    instanceBrandname = instance.BrandName

    if serialized.is_valid():
        BrandName = serialized.data['BrandName']
        Notes = serialized.data['Notes']
        Action = 'M'
        if not Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exclude(BrandName=instanceBrandname):
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exists():
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Edit', 'Brand already exists.', 'Brand name already exist in this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist in this branch"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Brand', 'Edit',
                     'Brand edited failed.', generate_serializer_errors(serialized._errors))

        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brands(request):
    from main.functions import get_location, get_device_name
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    # from django.contrib.gis.geoip2 import GeoIP2

    location = get_location(request)
    # device_name = get_device_name(request)
    print("###############")
    print(location)
    # print(device_name)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            if page_number and items_per_page:
                instances = Brand.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = Brand.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(ledger_sort_pagination)
            serialized = BrandRestSerializer(ledger_sort_pagination, many=True)

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information',
                         CreatedUserID, 'Brand', 'View', 'Brand list', 'brand not found')
            response_data = {
                "StatusCode": 6001,
                "message": "Brands Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information',
                     CreatedUserID, 'Brand', 'View', 'Brand list', 'brand not valid')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Brand.objects.filter(pk=pk).exists():
        instance = Brand.objects.get(pk=pk)
        serialized = BrandRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'User viewed a Brand')
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Brand Not Fount!"
        }

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'Brand not Found!')

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if pk == "1":
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand',
                     'Delete', 'Brand Deleted failed', 'Tried to Delete Default Brand!')
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Brand!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if Brand.objects.filter(pk=pk).exists():
            instance = Brand.objects.get(pk=pk)
        if instance:
            BranchID = instance.BranchID
            BrandID = instance.BrandID
            BrandName = instance.BrandName
            Notes = instance.Notes
            Action = "D"

            if not Product.objects.filter(BranchID=BranchID, BrandID=BrandID, CompanyID=CompanyID).exists():

                instance.delete()

                Brand_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=BrandID,
                    BrandName=BrandName,
                    Notes=Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                             'Delete', 'Brand Deleted Successfully', 'Brand Deleted Successfully')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Brand Deleted Successfully!"
                }
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand', 'Delete',
                             'Brand Deleted Failed', 'Brand Deleted Failed,Product has Created with this Brand')
                response_data = {
                    "StatusCode": 6001,
                    "message": "You can't Delete this Brand,Product exist with this Brand!!"
                }
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                         'Brand', 'Delete', 'Brand Deleted Failed', 'Brand Not Found!')
            response_data = {
                "StatusCode": 6001,
                "message": "Brand Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqry(request):

    from brands.models import SalesMaster, SalesDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)
    stockTrans_instance = StockTrans.objects.filter(
        CompanyID=CompanyID, VoucherType="SI", IsActive=True)
    for i in stockTrans_instance:
        BranchID = i.BranchID
        StockRateID = i.StockRateID

        stockRate_ins = StockRate.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, StockRateID=StockRateID)
        stockRate_ins.Qty = stockRate_ins.Qty + i.Qty
        stockRate_ins.save()
        i.IsActive = False
        i.save()

    stock_posting_ins = StockPosting.objects.filter(
        CompanyID=CompanyID, VoucherType="SI")
    for p in stock_posting_ins:
        p.delete()

    sales_master_ins = SalesMaster.objects.filter(CompanyID=CompanyID)
    VoucherType = "SI"

    for k in sales_master_ins:
        ledger_posting_ins = LedgerPosting.objects.filter(
            CompanyID=CompanyID, VoucherMasterID=k.SalesMasterID, VoucherType=VoucherType)
        for q in ledger_posting_ins:
            q.delete()

    for s in sales_master_ins:
        BranchID = s.BranchID
        SalesMasterID = s.SalesMasterID
        WarehouseID = s.WarehouseID
        sales_details_ins = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID)
        Action = s.Action
        CreatedDate = s.CreatedDate
        UpdatedDate = s.UpdatedDate
        CreatedUserID = s.CreatedUserID
        IsActive = s.IsActive

        VoucherNo = s.VoucherNo
        TotalGrossAmt = s.TotalGrossAmt
        Date = s.Date
        LedgerID = s.LedgerID

        LedgerPostingID = get_auto_LedgerPostid(
            LedgerPosting, BranchID, CompanyID)

        if SalesMasterID == 123:
            print("========--------------------------------========sales account")
        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=SalesMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=s.SalesAccount,
            Credit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=SalesMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=s.SalesAccount,
            Credit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        if float(s.TotalTax) > 0:
            print("========--------------------------------========totaltax>o")
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=55,
                Credit=s.TotalTax,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=55,
                Credit=s.TotalTax,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

        if float(s.TotalDiscount) > 0:
            print("========--------------------------------========TotalDiscount>o")
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=74,
                Debit=s.TotalDiscount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=74,
                Debit=s.TotalDiscount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

        if float(s.RoundOff) > 0:
            print("========--------------------------------========RoundOff>o")
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=78,
                Credit=s.RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=78,
                Credit=s.RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

        if float(s.RoundOff) < 0:
            print("========--------------------------------========RoundOff<o")
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            s.RoundOff = abs(float(s.RoundOff))

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=78,
                Debit=s.RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=SalesMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=78,
                Debit=s.RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

        account_group = AccountLedger.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

        if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
            print("========--------------------------------========usertable")
            DefaultAccountForUser = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
            Cash_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
            Bank_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            CashReceived = s.CashReceived
            BankAmount = s.BankAmount
            GrandTotal = s.GrandTotal
            Balance = s.Balance
            if CashReceived == 0E-8:
                CashReceived = 0
            if BankAmount == 0E-8:
                BankAmount = 0

            CashAmount = float(GrandTotal) - float(BankAmount)

            if DefaultAccountForUser:

                print(
                    "========--------------------------------========DefaultAccountForUser")
                if account_group == 9 and float(CashReceived) > 0 and float(BankAmount) > 0:
                    if SalesMasterID == 123:
                        print("##################1")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) > 0:
                    if SalesMasterID == 123:
                        print("##################2")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) > 0 and float(BankAmount) == 0:
                    if SalesMasterID == 123:
                        print("##################3")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) > 0:
                    if SalesMasterID == 123:
                        print("##################4")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) > 0:
                    if SalesMasterID == 123:
                        print("##################5")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) == 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) == 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) <= 0:
                    if SalesMasterID == 123:
                        print("##################7")
                        print(CashReceived)
                        print(BankAmount)
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) <= 0:
                    if SalesMasterID == 123:
                        print("##################8")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) <= 0:
                    if SalesMasterID == 123:
                        print("##################9")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) == 0:
                    if SalesMasterID == 123:
                        print("===================##################10yyyyy")
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) > 0:
                    cash = float(GrandTotal) - float(CashReceived)

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=cash,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=cash,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) > 0:
                    if SalesMasterID == 123:
                        print("##################11")
                    bank = float(GrandTotal) - float(BankAmount)
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=bank,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=bank,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )
            else:
                if SalesMasterID == 123:
                    print("==================##################12")
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

        for d in sales_details_ins:
            PriceListID_det = d.PriceListID
            PurchasePrice = PriceList.objects.get(
                PriceListID=PriceListID_det, BranchID=BranchID, CompanyID=CompanyID, ProductID=d.ProductID).PurchasePrice
            CostPerPrice = PurchasePrice
            d.CostPerPrice = CostPerPrice
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=d.PriceListID, BranchID=s.BranchID).MultiFactor
            PriceListID_DefUnit = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=d.ProductID, DefaultUnit=True, BranchID=s.BranchID).PriceListID
            qty = float(d.FreeQty) + float(d.Qty)
            Qty = float(MultiFactor) * float(qty)
            Cost = float(CostPerPrice) / float(MultiFactor)
            Qy = round(Qty, 4)
            Qty = str(Qy)
            Ct = round(Cost, 4)
            Cost = str(Ct)
            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=d.ProductID, PriceListID=PriceListID_DefUnit, BranchID=s.BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            changQty = Qty
            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=d.ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                stockRate_instances = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=d.ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                count = stockRate_instances.count()
                last = 0
                for stockRate_instance in stockRate_instances:
                    last = float(last) + float(1)
                    StockRateID = stockRate_instance.StockRateID
                    stock_post_cost = stockRate_instance.Cost

                    if float(stockRate_instance.Qty) > float(Qty):
                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) - float(Qty)
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                       VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(Qty)

                            stockPost_instance.QtyOut = newQty
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=s.Date,
                                VoucherMasterID=d.SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=d.ProductID,
                                BatchID=1,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=CreatedDate,
                                UpdatedDate=UpdatedDate,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=s.Date,
                                VoucherMasterID=d.SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=d.ProductID,
                                BatchID=1,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=CreatedDate,
                                UpdatedDate=UpdatedDate,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                        if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                            stockTra_in = StockTrans.objects.filter(
                                StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                            stockTra_in.Qty = float(
                                stockTra_in.Qty) + float(Qty)
                            stockTra_in.save()
                        else:
                            StockTransID = get_auto_StockTransID(
                                StockTrans, BranchID, CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=d.SalesDetailsID,
                                MasterID=d.SalesMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )
                    elif float(stockRate_instance.Qty) < float(Qty):

                        if float(changQty) > float(stockRate_instance.Qty):
                            changQty = float(changQty) - \
                                float(stockRate_instance.Qty)
                            stckQty = stockRate_instance.Qty
                            stockRate_instance.Qty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                           VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + \
                                    float(stockRate_instance.Qty)
                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=s.Date,
                                    VoucherMasterID=d.SalesMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=d.ProductID,
                                    BatchID=1,
                                    WareHouseID=WarehouseID,
                                    QtyOut=stckQty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=CreatedDate,
                                    UpdatedDate=UpdatedDate,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=s.Date,
                                    VoucherMasterID=d.SalesMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=d.ProductID,
                                    BatchID=1,
                                    WareHouseID=WarehouseID,
                                    QtyOut=stckQty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=CreatedDate,
                                    UpdatedDate=UpdatedDate,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )
                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(stockRate_instance.Qty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=d.SalesDetailsID,
                                    MasterID=d.SalesMasterID,
                                    Qty=stockRate_instance.Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )
                        else:
                            if changQty < 0:
                                changQty = 0
                            chqty = changQty
                            changQty = float(
                                stockRate_instance.Qty) - float(changQty)
                            stockRate_instance.Qty = changQty
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                           VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + float(chqty)
                                stockPost_instance.QtyOut = newQty
                                stockPost_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=s.Date,
                                    VoucherMasterID=d.SalesMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=d.ProductID,
                                    BatchID=1,
                                    WareHouseID=WarehouseID,
                                    QtyOut=chqty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=CreatedDate,
                                    UpdatedDate=UpdatedDate,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=s.Date,
                                    VoucherMasterID=d.SalesMasterID,
                                    VoucherType=VoucherType,
                                    ProductID=d.ProductID,
                                    BatchID=1,
                                    WareHouseID=WarehouseID,
                                    QtyOut=chqty,
                                    Rate=stock_post_cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=CreatedDate,
                                    UpdatedDate=UpdatedDate,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                stockTra_in = StockTrans.objects.filter(
                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                stockTra_in.Qty = float(
                                    stockTra_in.Qty) + float(chqty)
                                stockTra_in.save()
                            else:
                                StockTransID = get_auto_StockTransID(
                                    StockTrans, BranchID, CompanyID)
                                StockTrans.objects.create(
                                    StockTransID=StockTransID,
                                    BranchID=BranchID,
                                    VoucherType=VoucherType,
                                    StockRateID=StockRateID,
                                    DetailID=d.SalesDetailsID,
                                    MasterID=d.SalesMasterID,
                                    Qty=chqty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )

                    elif float(stockRate_instance.Qty) == float(Qty):
                        stockRate_instance.Qty = 0
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                       VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + \
                                float(Qty)
                            stockPost_instance.QtyOut = newQty
                            stockPost_instance.save()
                        else:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=s.Date,
                                VoucherMasterID=d.SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=d.ProductID,
                                BatchID=1,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=CreatedDate,
                                UpdatedDate=UpdatedDate,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=s.Date,
                                VoucherMasterID=d.SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=d.ProductID,
                                BatchID=1,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=stock_post_cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=CreatedDate,
                                UpdatedDate=UpdatedDate,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                        if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                            stockTra_in = StockTrans.objects.filter(
                                CompanyID=CompanyID, StockRateID=StockRateID, DetailID=d.SalesDetailsID, MasterID=d.SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                            stockTra_in.Qty = float(
                                stockTra_in.Qty) + float(Qty)
                            stockTra_in.save()
                        else:
                            StockTransID = get_auto_StockTransID(
                                StockTrans, BranchID, CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=d.SalesDetailsID,
                                MasterID=d.SalesMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=d.ProductID, Cost=Cost, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                stockRate_instance = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=d.ProductID, Cost=Cost, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                stock_post_cost = stockRate_instance.Cost
                if float(changQty) > 0:
                    stockRate_instance.Qty = float(
                        stockRate_instance.Qty) - float(changQty)
                    stockRate_instance.save()

                    if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                   VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=d.ProductID, BranchID=BranchID,
                                                                      VoucherMasterID=d.SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        QtyOut = stockPost_instance.QtyOut
                        newQty = float(QtyOut) + float(changQty)
                        stockPost_instance.QtyOut = newQty
                        stockPost_instance.save()
                    else:
                        StockPostingID = get_auto_stockPostid(
                            StockPosting, BranchID, CompanyID)
                        StockPosting.objects.create(
                            StockPostingID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=s.Date,
                            VoucherMasterID=d.SalesMasterID,
                            VoucherType=VoucherType,
                            ProductID=d.ProductID,
                            BatchID=1,
                            WareHouseID=WarehouseID,
                            QtyOut=changQty,
                            Rate=stock_post_cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=s.Date,
                            VoucherMasterID=d.SalesMasterID,
                            VoucherType=VoucherType,
                            ProductID=d.ProductID,
                            BatchID=1,
                            WareHouseID=WarehouseID,
                            QtyOut=changQty,
                            Rate=stock_post_cost,
                            PriceListID=PriceListID_DefUnit,
                            IsActive=IsActive,
                            CreatedDate=CreatedDate,
                            UpdatedDate=UpdatedDate,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                    if not StockTrans.objects.filter(CompanyID=CompanyID,
                                                     StockRateID=stockRate_instance.StockRateID,
                                                     DetailID=d.SalesDetailsID,
                                                     MasterID=d.SalesMasterID,
                                                     VoucherType=VoucherType,
                                                     BranchID=BranchID).exists():

                        StockTransID = get_auto_StockTransID(
                            StockTrans, BranchID, CompanyID)
                        StockTrans.objects.create(
                            CompanyID=CompanyID,
                            StockTransID=StockTransID,
                            BranchID=BranchID,
                            VoucherType=VoucherType,
                            StockRateID=stockRate_instance.StockRateID,
                            DetailID=d.SalesDetailsID,
                            MasterID=d.SalesMasterID,
                            Qty=changQty,
                            IsActive=IsActive
                        )
            else:
                if float(changQty) > 0:
                    qty = float(Qty) * -1
                    StockRateID = get_auto_StockRateID(
                        StockRate, BranchID, CompanyID)
                    StockRate.objects.create(
                        StockRateID=StockRateID,
                        BranchID=BranchID,
                        BatchID=1,
                        PurchasePrice=PurchasePrice,
                        SalesPrice=SalesPrice,
                        Qty=qty,
                        Cost=Cost,
                        ProductID=d.ProductID,
                        WareHouseID=WarehouseID,
                        Date=s.Date,
                        PriceListID=PriceListID_DefUnit,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CompanyID=CompanyID,
                    )

                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)
                    StockPosting.objects.create(
                        StockPostingID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=s.Date,
                        VoucherMasterID=d.SalesMasterID,
                        VoucherType=VoucherType,
                        ProductID=d.ProductID,
                        BatchID=1,
                        WareHouseID=WarehouseID,
                        QtyOut=qty,
                        Rate=Cost,
                        PriceListID=PriceListID_DefUnit,
                        IsActive=IsActive,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    StockPosting_Log.objects.create(
                        TransactionID=StockPostingID,
                        BranchID=BranchID,
                        Action=Action,
                        Date=s.Date,
                        VoucherMasterID=d.SalesMasterID,
                        VoucherType=VoucherType,
                        ProductID=d.ProductID,
                        BatchID=1,
                        WareHouseID=WarehouseID,
                        QtyOut=qty,
                        Rate=Cost,
                        PriceListID=PriceListID_DefUnit,
                        IsActive=IsActive,
                        CreatedDate=CreatedDate,
                        UpdatedDate=UpdatedDate,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                    StockTransID = get_auto_StockTransID(
                        StockTrans, BranchID, CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=d.SalesDetailsID,
                        MasterID=d.SalesMasterID,
                        Qty=qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                    )
            d.save()

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryBillDiscAmt(request):

    from brands.models import SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    sales_master_ins = SalesMaster.objects.filter(CompanyID=CompanyID)

    for s in sales_master_ins:
        if s.BillDiscAmt > 0:
            s.TotalDiscount = s.BillDiscAmt
            s.save()

    purchase_master_ins = PurchaseMaster.objects.filter(CompanyID=CompanyID)

    for s in purchase_master_ins:
        if s.BillDiscAmt > 0:
            s.TotalDiscount = s.BillDiscAmt
            s.save()

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryPurchase(request):

    from brands.models import PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    stockTrans_instance = StockTrans.objects.filter(
        CompanyID=CompanyID, VoucherType="PI", IsActive=True)
    for i in stockTrans_instance:
        BranchID = i.BranchID
        StockRateID = i.StockRateID

        stockRate_ins = StockRate.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, StockRateID=StockRateID)
        stockRate_ins.Qty = stockRate_ins.Qty - i.Qty
        stockRate_ins.save()
        i.IsActive = False
        i.save()

    stock_posting_ins = StockPosting.objects.filter(
        CompanyID=CompanyID, VoucherType="PI")
    for p in stock_posting_ins:
        p.delete()

    purchase_master_ins = PurchaseMaster.objects.filter(CompanyID=CompanyID)
    VoucherType = "PI"

    for k in purchase_master_ins:
        ledger_posting_ins = LedgerPosting.objects.filter(
            CompanyID=CompanyID, VoucherMasterID=k.PurchaseMasterID, VoucherType=VoucherType)
        for q in ledger_posting_ins:
            q.delete()

    for s in purchase_master_ins:
        BranchID = s.BranchID
        PurchaseMasterID = s.PurchaseMasterID
        WarehouseID = s.WarehouseID
        purchase_details_ins = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID)
        Action = s.Action
        CreatedDate = s.CreatedDate
        UpdatedDate = s.UpdatedDate
        CreatedUserID = s.CreatedUserID
        IsActive = s.IsActive

        VoucherNo = s.VoucherNo
        TotalGrossAmt = s.TotalGrossAmt
        GrandTotal = s.GrandTotal
        Date = s.Date
        LedgerID = s.LedgerID

        LedgerPostingID = get_auto_LedgerPostid(
            LedgerPosting, BranchID, CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=s.PurchaseAccount,
            Debit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=s.PurchaseAccount,
            Debit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        LedgerPostingID = get_auto_LedgerPostid(
            LedgerPosting, BranchID, CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=LedgerID,
            Credit=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CompanyID=CompanyID,
        )

        if float(s.TotalDiscount) > 0:

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=83,
                Credit=s.TotalDiscount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=83,
                Credit=s.TotalDiscount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

        for d in purchase_details_ins:

            ProductID = d.ProductID

            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=d.PriceListID, BranchID=BranchID).MultiFactor
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

            qty = float(d.FreeQty) + float(d.Qty)

            Qty = float(MultiFactor) * float(qty)
            Cost = float(d.CostPerItem) / float(MultiFactor)

            Qy = round(Qty, 4)
            Qty = str(Qy)

            Ct = round(Cost, 4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            StockPostingID = get_auto_stockPostid(
                StockPosting, BranchID, CompanyID)

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=1,
                WareHouseID=s.WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=1,
                WareHouseID=s.WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            stockRateInstance = None

            WarehouseID = s.WarehouseID
            PurchaseDetailsID = d.PurchaseDetailsID

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(
                    stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(
                        StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(
                        StockTrans, BranchID, CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=PurchaseDetailsID,
                        MasterID=PurchaseMasterID,
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                    )

            else:
                StockRateID = get_auto_StockRateID(
                    StockRate, BranchID, CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    BatchID=1,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=Qty,
                    Cost=Cost,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
                    Date=Date,
                    PriceListID=PriceListID,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

                StockTransID = get_auto_StockTransID(
                    StockTrans, BranchID, CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseDetailsID,
                    MasterID=PurchaseMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                )

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryOpeningStock(request):

    from brands.models import OpeningStockMaster, OpeningStockDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    stockTrans_instance = StockTrans.objects.filter(
        CompanyID=CompanyID, VoucherType="OS", IsActive=True)
    for i in stockTrans_instance:
        BranchID = i.BranchID
        StockRateID = i.StockRateID

        stockRate_ins = StockRate.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, StockRateID=StockRateID)
        stockRate_ins.Qty = stockRate_ins.Qty - i.Qty
        stockRate_ins.save()
        i.IsActive = False
        i.save()

    stock_posting_ins = StockPosting.objects.filter(
        CompanyID=CompanyID, VoucherType="OS")
    for p in stock_posting_ins:
        p.delete()

    openingStock_master_ins = OpeningStockMaster.objects.filter(
        CompanyID=CompanyID)
    VoucherType = "OS"

    for s in openingStock_master_ins:
        BranchID = s.BranchID
        OpeningStockMasterID = s.OpeningStockMasterID
        WarehouseID = s.WarehouseID
        openingStock_details_ins = OpeningStockDetails.objects.filter(
            CompanyID=CompanyID, OpeningStockMasterID=OpeningStockMasterID)
        Action = s.Action
        CreatedDate = s.CreatedDate
        UpdatedDate = s.UpdatedDate
        CreatedUserID = s.CreatedUserID
        IsActive = s.IsActive

        VoucherNo = s.VoucherNo
        GrandTotal = s.GrandTotal
        Date = s.Date

        for d in openingStock_details_ins:

            ProductID = d.ProductID
            OpeningStockDetailsID = d.OpeningStockDetailsID

            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=d.PriceListID, BranchID=BranchID).MultiFactor
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            # qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(d.Qty)
            Cost = float(d.Rate) / float(MultiFactor)

            Qy = round(Qty, 4)
            Qty = str(Qy)

            Ct = round(Cost, 4)
            Cost = str(Ct)

            StockPostingID = get_auto_stockPostid(
                StockPosting, BranchID, CompanyID)
            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=OpeningStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=1,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=OpeningStockMasterID,
                VoucherType=VoucherType,
                ProductID=ProductID,
                BatchID=1,
                WareHouseID=WarehouseID,
                QtyIn=Qty,
                Rate=Cost,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(
                    stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                StockTransID = get_auto_StockTransID(
                    StockTrans, BranchID, CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=OpeningStockDetailsID,
                    MasterID=OpeningStockMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                )
            else:
                StockRateID = get_auto_StockRateID(
                    StockRate, BranchID, CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    BatchID=1,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=Qty,
                    Cost=Cost,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
                    Date=Date,
                    PriceListID=PriceListID,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

                StockTransID = get_auto_StockTransID(
                    StockTrans, BranchID, CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=OpeningStockDetailsID,
                    MasterID=OpeningStockMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                )

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryPyment(request):

    from brands.models import PaymentMaster, PaymentDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    payment_master_ins = PaymentMaster.objects.filter(CompanyID=CompanyID)

    for k in payment_master_ins:
        ledger_posting_ins = LedgerPosting.objects.filter(
            CompanyID=CompanyID, VoucherMasterID=k.PaymentMasterID, VoucherType=k.VoucherType)
        for q in ledger_posting_ins:
            q.delete()
    for p in payment_master_ins:
        PaymentMasterID = p.PaymentMasterID
        BranchID = p.BranchID
        Date = p.Date
        VoucherType = p.VoucherType
        VoucherNo = p.VoucherNo
        IsActive = p.IsActive
        Action = p.Action
        CreatedUserID = p.CreatedUserID
        CreatedDate = p.CreatedDate
        UpdatedDate = p.UpdatedDate
        MasterLedgerID = p.LedgerID
        payment_detail_ins = PaymentDetails.objects.filter(
            PaymentMasterID=PaymentMasterID, CompanyID=CompanyID)

        for d in payment_detail_ins:
            PaymentDetailsID = d.PaymentDetailsID
            LedgerID = d.LedgerID
            Amount = d.Amount
            NetAmount = d.NetAmount
            Discount = d.Discount

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=LedgerID,
                Debit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                Credit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Credit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            if float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=82,
                    Credit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=82,
                    Credit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryReciept(request):

    from brands.models import ReceiptMaster, ReceiptDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    receipt_master_ins = ReceiptMaster.objects.filter(CompanyID=CompanyID)

    for k in receipt_master_ins:
        ledger_posting_ins = LedgerPosting.objects.filter(
            CompanyID=CompanyID, VoucherMasterID=k.ReceiptMasterID, VoucherType=k.VoucherType)
        for q in ledger_posting_ins:
            q.delete()
    for p in receipt_master_ins:
        ReceiptMasterID = p.ReceiptMasterID
        BranchID = p.BranchID
        Date = p.Date
        VoucherType = p.VoucherType
        VoucherNo = p.VoucherNo
        IsActive = p.IsActive
        Action = p.Action
        CreatedUserID = p.CreatedUserID
        CreatedDate = p.CreatedDate
        UpdatedDate = p.UpdatedDate
        MasterLedgerID = p.LedgerID
        receipt_detail_ins = ReceiptDetails.objects.filter(
            ReceiptMasterID=ReceiptMasterID, CompanyID=CompanyID)

        for d in receipt_detail_ins:
            ReceiptDetailID = d.ReceiptDetailID
            LedgerID = d.LedgerID
            Amount = d.Amount
            NetAmount = d.NetAmount
            Discount = d.Discount

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=LedgerID,
                Credit=Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
                Debit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Debit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=CreatedDate,
                UpdatedDate=UpdatedDate,
                CompanyID=CompanyID,
            )

            if float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=72,
                    Debit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=72,
                    Debit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=CreatedDate,
                    UpdatedDate=UpdatedDate,
                    CompanyID=CompanyID,
                )

    print("=======================================================")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryTest(request):

    from brands.models import SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, ReceiptDetails,LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log,PaymentDetails
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    # CompanyID = "2064907b-3dd6-4efe-a449-d2f3ad4bf9c4"
    CompanyID = "8cd7e0b6-72f0-494e-b0ae-8f903080e00e"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    BranchID = 1

    cash_payments_ins = PaymentDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    
    for i in cash_payments_ins:
        PaymentDetailsID = i.PaymentDetailsID
        PaymentMasterID = i.PaymentMasterID
        LedgerID = i.LedgerID
        VoucherType = i.VoucherType
        print("here we goooooooooooooooooo")
        if not LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PaymentMasterID,VoucherDetailID=PaymentDetailsID,LedgerID=LedgerID,VoucherType=VoucherType).exists():
            print("=====================================payments")
            print(PaymentMasterID)
            print(PaymentDetailsID)
            print(LedgerID)
            print("##################uuuuuu")


    cash_receipts_ins = ReceiptDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    
    for t in cash_receipts_ins:
        ReceiptDetailID = t.ReceiptDetailID
        ReceiptMasterID = t.ReceiptMasterID
        LedgerID = t.LedgerID
        VoucherType = t.VoucherType
        print("here we goooooooooooooooooo2222")
        if not LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=ReceiptMasterID,VoucherDetailID=ReceiptDetailID,LedgerID=LedgerID,VoucherType=VoucherType).exists():
            print("=====================================receipts")
            print(ReceiptMasterID)
            print(ReceiptDetailID)
            print(LedgerID)
            print("##################vvvvv")




    print("------------------------->.................>>>>>>>>>>>>>>>>>>>>>......suucess")

    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryForPriceList(request):

    from brands.models import SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log, OpeningStockDetails
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    BranchID = 1

    salesDetails_ins = SalesDetails.objects.filter(CompanyID=CompanyID)
    for i in salesDetails_ins:
        UnitID = i.PriceListID
        ProductID = i.ProductID

        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID).exists():
            pricelist_ins = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID)
            for p in pricelist_ins:
                PriceListID = p.PriceListID

                i.PriceListID = PriceListID

                i.save()

    print("Sales finished successfully---------------")

    purchaseDetails_ins = PurchaseDetails.objects.filter(CompanyID=CompanyID)
    for i in purchaseDetails_ins:
        UnitID = i.PriceListID
        ProductID = i.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID).exists():
            pricelist_ins = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID)
            for p in pricelist_ins:
                PriceListID = p.PriceListID

                i.PriceListID = PriceListID

                i.save()

    print("Purchase finished successfully---------------")

    openingStockDetails_ins = OpeningStockDetails.objects.filter(
        CompanyID=CompanyID)
    for i in openingStockDetails_ins:
        UnitID = i.PriceListID
        ProductID = i.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID).exists():
            pricelist_ins = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, UnitID=UnitID)
            for p in pricelist_ins:
                PriceListID = p.PriceListID

                i.PriceListID = PriceListID

                i.save()

    print("Opening stock finished successfully---------------")

    # PurchasePrice = PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=PriceListID).PurchasePrice
    # i.CostPerPrice = PurchasePrice

    # i.save()

    print("------------------------->.................>>>>>>>>>>>>>>>>>>>>>......suucess")

    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def torunqryProductUpdate(request):

    from brands.models import SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting, AccountLedger, UserTable, LedgerPosting_Log, Product
    from api.v4.sales.functions import get_auto_stockPostid
    from api.v4.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v4.accountLedgers.functions import get_auto_LedgerPostid

    CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    CompanyID = CompanySettings.objects.get(id=CompanyID)

    BranchID = 1

    # product_ins = Product.objects.filter(CompanyID=CompanyID)
    product_ins = Product.objects.all()
    for i in product_ins:
        i.IsSales = True
        i.IsPurchase = True
        i.Active = True
        i.InventoryType = "StockItem"
        i.save()
    print("--------------------------------------success")
    response_data = {
        "StatusCode": 6000,
        "message": "success"
    }

    return Response(response_data, status=status.HTTP_200_OK)


# from django.contrib import messages
# from django.views.generic.edit import FormView
# from django.shortcuts import redirect

# from .forms import GenerateRandomUserForm


# class GenerateRandomUserView(FormView):
#     template_name = 'core/generate_random_users.html'
#     form_class = GenerateRandomUserForm

#     def form_valid(self, form):
#         total = form.cleaned_data.get('total')
#         create_random_user_accounts.delay(total)
#         messages.success(
#             self.request, 'We are generating your random users! Wait a moment and refresh this page.')
#         return redirect('users_list')


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def generate_random_users(request):
    total = int(request.data['total'])
    print(total)
    create_random_user_accounts.delay(int(total))

    response_data = {
        "StatusCode": 6000,
        "message": "users generated successfully",
        "total": total,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_brands(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = Brand.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "BrandName":
                    instances = instances.filter(
                        (Q(BrandName__icontains=product_name)))[:10]
            else:
                if param == "BrandName":
                    instances = instances.filter(
                        (Q(BrandName__icontains=product_name)))

            serialized = BrandRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
