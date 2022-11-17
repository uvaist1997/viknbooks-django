from api.v3.brands.tasks import create_random_user_accounts
from django.contrib.auth.models import User
from brands.models import Brand, Brand_Log, Product, Activity_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.brands.serializers import BrandSerializer, BrandRestSerializer, ListSerializer
from api.v3.brands.functions import generate_serializer_errors
from rest_framework import status
from api.v3.brands.functions import get_auto_id
from main.functions import get_company, activity_log
import datetime


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
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    from main.functions import get_location, get_device_name
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
            instances = Brand.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = BrandRestSerializer(instances, many=True)

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
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
    from api.v3.sales.functions import get_auto_stockPostid
    from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v3.accountLedgers.functions import get_auto_LedgerPostid

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
    from api.v3.sales.functions import get_auto_stockPostid
    from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v3.accountLedgers.functions import get_auto_LedgerPostid

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
    from api.v3.sales.functions import get_auto_stockPostid
    from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v3.accountLedgers.functions import get_auto_LedgerPostid

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
    from api.v3.sales.functions import get_auto_stockPostid
    from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v3.accountLedgers.functions import get_auto_LedgerPostid

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
def torunqryTest(request):

    from brands.models import SalesMaster, SalesDetails, PurchaseMaster, PurchaseDetails, PriceList, StockRate, StockPosting, StockTrans, StockPosting_Log, CompanySettings, LedgerPosting,\
    TransactionTypes, CompanySettings, GeneralSettings, AccountLedger, UserTable, LedgerPosting_Log,JournalMaster,JournalDetails,Parties,Bank,PaymentMaster,\
    ReceiptMaster, PurchaseReturnMaster,SalesReturnMaster
    from api.v3.sales.functions import get_auto_stockPostid
    from api.v3.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
    from api.v3.accountLedgers.functions import get_auto_LedgerPostid

    # CompanyID = "8ecd67fb-e2f4-4da0-b6ce-2b14127e3459"
    # CompanyID = "6d9a2f1f-73d6-42d1-9d0f-8b957766263c"
    print("starts==============================================================start")
    companies = CompanySettings.objects.all()
    BranchID = 1
    for c in companies:
        CompanyID = c
        if LedgerPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID):
            ledger_posting_ins = LedgerPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for lpi in ledger_posting_ins:
                lpi.delete()

        if AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            ledger_ins = AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for li in ledger_ins:
                OpeningBalance = li.OpeningBalance
                CrOrDr = li.CrOrDr
                today = li.CreatedDate
                LedgerCode = li.LedgerCode
                LedgerID = li.LedgerID
                CreatedUserID = li.CreatedUserID
                IsActive = li.IsActive
                Action = li.Action
                if float(OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=LedgerCode,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=LedgerCode,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

        print("accountLedger==============================================================accountLedger")

        if Parties.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            party_ins = Parties.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for pins in party_ins:
                LedgerID = pins.LedgerID
                PartyCode = pins.PartyCode
                if AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID,LedgerCode=PartyCode).exists():
                    party_ledger_ins = AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID,LedgerCode=PartyCode)
                    OpeningBalance = party_ledger_ins.OpeningBalance
                    CrOrDr = party_ledger_ins.CrOrDr
                    VoucherType = "LOB"
                    today = party_ledger_ins.CreatedDate
                    IsActive = party_ledger_ins.IsActive
                    Action = party_ledger_ins.Action
                    CreatedUserID = party_ledger_ins.CreatedUserID
                    if float(OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrOrDr == "Cr":
                            Credit = OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

        print("parties==============================================================parties")
        if Bank.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            bank_ins = Bank.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for bins in bank_ins:
                LedgerCode = bins.LedgerCode
                if AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerCode=LedgerCode).exists():
                    bank_ledger_ins = AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerCode=LedgerCode)
                    OpeningBalance = bank_ledger_ins.OpeningBalance
                    CrOrDr = bank_ledger_ins.CrOrDr
                    VoucherType = "LOB"
                    today = bank_ledger_ins.CreatedDate
                    IsActive = bank_ledger_ins.IsActive
                    Action = bank_ledger_ins.Action
                    CreatedUserID = bank_ledger_ins.CreatedUserID
                    LedgerID = bank_ledger_ins.LedgerID
                    if float(OpeningBalance) > 0:
                        Credit = 0.00
                        Debit = 0.00

                        if CrOrDr == "Cr":
                            Credit = OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

        print("payments==============================================================payments")
        if PaymentMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            payments_ins = PaymentMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for pay_ins in payments_ins:
                PaymentMasterID = pay_ins.pay_ins.PaymentMasterID
                VoucherNo = pay_ins.VoucherNo
                VoucherType = pay_ins.VoucherType
                Date = pay_ins.Date
                MasterLedgerID = pay_ins.LedgerID
                IsActive = pay_ins.IsActive
                Action = pay_ins.Action
                CreatedUserID = pay_ins.CreatedUserID
                today = pay_ins.CreatedDate
                if PaymentDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PaymentMasterID=PaymentMasterID).exists():
                    pay_detail_ins = PaymentDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PaymentMasterID=PaymentMasterID)

                    for payD in pay_detail_ins:
                        PaymentDetailsID = payD.PaymentDetailsID
                        LedgerID = PaymentDetailsID.LedgerID
                        Amount = PaymentDetailsID.Amount
                        NetAmount = PaymentDetailsID.NetAmount
                        Discount = PaymentDetailsID.Discount
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

        print("receipts==============================================================receipts")
        if ReceiptMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            payments_ins = ReceiptMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for pay_ins in payments_ins:
                ReceiptMasterID = pay_ins.ReceiptMasterID
                VoucherNo = pay_ins.VoucherNo
                VoucherType = pay_ins.VoucherType
                Date = pay_ins.Date
                MasterLedgerID = pay_ins.LedgerID
                IsActive = pay_ins.IsActive
                Action = pay_ins.Action
                CreatedUserID = pay_ins.CreatedUserID
                today = pay_ins.CreatedDate
                if ReceiptDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ReceiptMasterID=ReceiptMasterID).exists():
                    pay_detail_ins = ReceiptDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ReceiptMasterID=ReceiptMasterID)

                    for payD in pay_detail_ins:
                        ReceiptDetailID = payD.ReceiptDetailID
                        LedgerID = PaymentDetailsID.LedgerID
                        Amount = PaymentDetailsID.Amount
                        NetAmount = PaymentDetailsID.NetAmount
                        Discount = PaymentDetailsID.Discount

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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

        print("journal==============================================================journal")
        if JournalMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            journal_ins = JournalMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for jr in journal_ins:
                JournalMasterID = jr.JournalMasterID
                VoucherNo = jr.VoucherNo
                Date = jr.Date
                IsActive = jr.IsActive
                Action = jr.Action
                CreatedUserID = jr.CreatedUserID
                today = jr.CreatedDate
                VoucherType = "JL"
                if JournalDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,JournalMasterID=JournalMasterID).exists():
                    joun_ins = JournalDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,JournalMasterID=JournalMasterID)
                    for jnD in joun_ins:
                        LedgerID = jnD.LedgerID
                        Debit = jnD.Debit
                        Credit = jnD.Credit
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=JournalMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=JournalMasterID,
                            VoucherNo=VoucherNo,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

        print("purchase==============================================================purchase")

        if PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            purch_ins = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for pr in purch_ins:
                VoucherType = "PI"
                PurchaseMasterID = pr.PurchaseMasterID
                VoucherNo = pr.VoucherNo
                Date = pr.Date
                PurchaseAccount = pr.PurchaseAccount
                TotalGrossAmt = pr.TotalGrossAmt
                IsActive = pr.IsActive
                Action = pr.Action
                CreatedUserID = pr.CreatedUserID
                today = pr.CreatedDate
                TaxType = pr.TaxType
                VATAmount = pr.VATAmount
                SGSTAmount = pr.SGSTAmount
                CGSTAmount = pr.CGSTAmount
                IGSTAmount = pr.IGSTAmount
                TAX1Amount = pr.TAX1Amount
                TAX2Amount = pr.TAX2Amount
                TAX3Amount = pr.TAX3Amount
                TotalDiscount = pr.TotalDiscount
                RoundOff = pr.RoundOff
                LedgerID = pr.LedgerID
                CashReceived = pr.CashReceived
                BankAmount = pr.BankAmount
                GrandTotal = pr.GrandTotal
                CashAmount = pr.CashAmount
                Balance = pr.Balance

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    Debit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    Debit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )


                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                elif TaxType == 'GST Intra-state B2B':
                    if float(SGSTAmount) > 0 or float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            LedgerID=42,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=42,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                elif TaxType == 'GST Inter-state B2B':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                elif not TaxType == 'Import' and not TaxType == 'VAT':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if float(TotalDiscount) > 0:

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
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
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
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                    DefaultAccountForUser = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
                    Cash_Account = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                    Bank_Account = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

                    AllowCashReceiptMorePurchaseAmt = False
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowCashReceiptMorePurchaseAmt").exists():
                        AllowCashReceiptMorePurchaseAmt = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="AllowCashReceiptMorePurchaseAmt").SettingsValue
                        if AllowCashReceiptMorePurchaseAmt == "True" or AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                            AllowCashReceiptMorePurchaseAmt = True

                    if DefaultAccountForUser:
                        if account_group == 9 and float(CashReceived) > 0 and float(BankAmount) > 0:
                            CashAmount = float(GrandTotal) - float(BankAmount)
                            if float(CashAmount) < float(CashReceived):
                                CashAmount = CashReceived
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
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) > 0:
                            LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)
                            LedgerPosting.objects.create(
                                LedgerPostingID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=GrandTotal,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=GrandTotal,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 9 and float(CashReceived) > 0 and float(BankAmount) == 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )
                        elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )
                        elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Cash_Account,
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) > 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) == 0:

                            LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)
                            LedgerPosting.objects.create(
                                LedgerPostingID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=GrandTotal,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=GrandTotal,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) == 0:

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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) <= 0:
                            LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)
                            LedgerPosting.objects.create(
                                LedgerPostingID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            if AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                                LedgerPostingID = get_auto_LedgerPostid(
                                    LedgerPosting, BranchID, CompanyID)
                                LedgerPosting.objects.create(
                                    LedgerPostingID=LedgerPostingID,
                                    BranchID=BranchID,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherType=VoucherType,
                                    VoucherNo=VoucherNo,
                                    LedgerID=Cash_Account,
                                    Credit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                                LedgerPosting_Log.objects.create(
                                    TransactionID=LedgerPostingID,
                                    BranchID=BranchID,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherType=VoucherType,
                                    VoucherNo=VoucherNo,
                                    LedgerID=Cash_Account,
                                    Credit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                                BankCash = float(BankAmount) + float(CashReceived)
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
                                    Debit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Debit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                            else:
                                if (float(CashReceived) + float(BankAmount)) >= float(GrandTotal):
                                    if float(BankAmount) == float(GrandTotal):
                                        CashAmount = 0
                                    elif float(BankAmount) < float(GrandTotal):
                                        CashAmount = float(GrandTotal) - float(BankAmount)
                                    elif (float(CashReceived) + float(BankAmount)) < float(GrandTotal):
                                        CashAmount = CashReceived

                                LedgerPostingID = get_auto_LedgerPostid(
                                    LedgerPosting, BranchID, CompanyID)
                                LedgerPosting.objects.create(
                                    LedgerPostingID=LedgerPostingID,
                                    BranchID=BranchID,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherType=VoucherType,
                                    VoucherNo=VoucherNo,
                                    LedgerID=Cash_Account,
                                    Credit=CashAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                                LedgerPosting_Log.objects.create(
                                    TransactionID=LedgerPostingID,
                                    BranchID=BranchID,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherType=VoucherType,
                                    VoucherNo=VoucherNo,
                                    LedgerID=Cash_Account,
                                    Credit=CashAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                              

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) <= 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            if AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                                BankCash = float(BankAmount) + float(CashReceived)
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
                                    Debit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Debit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                            else:
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
                                    Debit=BankAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Debit=BankAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) <= 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Cash_Account,
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            

                            if AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                                # BankCash = float(BankAmount) + float(CashReceived)
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
                                    Debit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Debit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                            else:
                                total = float(GrandTotal) + float(Balance)
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
                                    Debit=total,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Debit=total,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) > 0:
                            # cash = float(GrandTotal) - float(CashReceived)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Cash_Account,
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) > 0:
                            # bank = float(GrandTotal) - float(BankAmount)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) > 0:
                            # bank = float(GrandTotal) - float(BankAmount)
                            cash_bank = float(BankAmount) + float(CashAmount)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Cash_Account,
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Cash_Account,
                                Credit=CashAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            LedgerPosting_Log.objects.create(
                                TransactionID=LedgerPostingID,
                                BranchID=BranchID,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherType=VoucherType,
                                VoucherNo=VoucherNo,
                                LedgerID=Bank_Account,
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=cash_bank,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=cash_bank,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                    else:
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

        print("sales==============================================================sales")
        if SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            sales_inst = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for st in sales_inst:
                VoucherType = "SI"
                VoucherNo = st.VoucherNo
                Date = st.Date
                SalesMasterID = st.SalesMasterID
                SalesAccount = st.SalesAccount
                TotalGrossAmt = st.TotalGrossAmt
                IsActive = st.IsActive
                Action = st.Action
                CreatedUserID = st.CreatedUserID
                today = st.CreatedDate
                TaxType = st.TaxType
                VATAmount = st.VATAmount
                SGSTAmount = st.SGSTAmount
                CGSTAmount = st.CGSTAmount
                IGSTAmount = st.IGSTAmount
                TAX1Amount = st.TAX1Amount
                TAX2Amount = st.TAX2Amount
                TAX3Amount = st.TAX3Amount
                TotalDiscount = st.TotalDiscount
                RoundOff = st.RoundOff
                LedgerID = st.LedgerID
                CashReceived = st.CashReceived
                BankAmount = st.BankAmount
                GrandTotal = st.GrandTotal
                CashAmount = st.CashAmount
                Balance = st.Balance
                KFCAmount = st.KFCAmount

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    Credit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    Credit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                if TaxType == 'VAT':
                    if float(VATAmount) > 0:

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
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if float(SGSTAmount) > 0 or float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            LedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if TaxType == 'GST Intra-state B2C':
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                if not TaxType == 'Export':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if float(TotalDiscount) > 0:

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
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
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
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) > 0:

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
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
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
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
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
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                    DefaultAccountForUser = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
                    Cash_Account = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                    Bank_Account = UserTable.objects.get(
                        CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

                    AllowCashReceiptMoreSaleAmt = False
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowCashReceiptMoreSaleAmt").exists():
                        AllowCashReceiptMoreSaleAmt = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="AllowCashReceiptMoreSaleAmt").SettingsValue
                        if AllowCashReceiptMoreSaleAmt == "True" or AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                            AllowCashReceiptMoreSaleAmt = True

                    if DefaultAccountForUser:
                        if account_group == 9 and float(CashReceived) > 0 and float(BankAmount) > 0:
                            CashAmount = float(GrandTotal) - float(BankAmount)
                            if float(CashAmount) < float(CashReceived):
                                CashAmount = CashReceived
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) > 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 9 and float(CashReceived) > 0 and float(BankAmount) == 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )
                        elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) > 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) <= 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
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
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                                BankCash = float(BankAmount) + float(CashReceived)
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
                                    Credit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Credit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                            else:
                                if (float(CashReceived) + float(BankAmount)) >= float(GrandTotal):
                                    if float(BankAmount) == float(GrandTotal):
                                        CashAmount = 0
                                    elif float(BankAmount) < float(GrandTotal):
                                        CashAmount = float(GrandTotal) - float(BankAmount)
                                    elif (float(CashReceived) + float(BankAmount)) < float(GrandTotal):
                                        CashAmount = CashReceived

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
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) <= 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                                BankCash = float(BankAmount) + float(CashReceived)
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
                                    Credit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Credit=BankCash,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                            else:
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
                                    Credit=BankAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Credit=BankAmount,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) <= 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            

                            if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                                # BankCash = float(BankAmount) + float(CashReceived)
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
                                    Credit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Credit=CashReceived,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                            else:
                                total = float(GrandTotal) + float(Balance)
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
                                    Credit=total,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
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
                                    Credit=total,
                                    IsActive=IsActive,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) > 0:
                            # cash = float(GrandTotal) - float(CashReceived)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Debit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=CashReceived,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) > 0:
                            # bank = float(GrandTotal) - float(BankAmount)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=BankAmount,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                        elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) > 0:
                            # bank = float(GrandTotal) - float(BankAmount)
                            cash_bank = float(BankAmount) + float(CashAmount)
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=cash_bank,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
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
                                Credit=cash_bank,
                                IsActive=IsActive,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                    else:
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
                            CreatedDate=today,
                            UpdatedDate=today,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

        print("purchaseReturn==============================================================purchaseReturn")
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            purchsRet_inst = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for srt in purchsRet_inst:
                PurchaseReturnMasterID = srt.PurchaseReturnMasterID
                VoucherNo = srt.VoucherNo
                VoucherDate = srt.VoucherDate
                PurchaseAccount = srt.PurchaseAccount
                TotalGrossAmt = srt.TotalGrossAmt
                IsActive = srt.IsActive
                Action = srt.Action
                CreatedUserID = srt.CreatedUserID
                today = srt.CreatedDate
                TaxType = srt.TaxType
                VATAmount = srt.VATAmount
                SGSTAmount = srt.SGSTAmount
                CGSTAmount = srt.CGSTAmount
                IGSTAmount = srt.IGSTAmount
                TAX1Amount = srt.TAX1Amount
                TAX2Amount = srt.TAX2Amount
                TAX3Amount = srt.TAX3Amount
                TotalDiscount = srt.TotalDiscount
                RoundOff = srt.RoundOff
                LedgerID = srt.LedgerID
                # CashReceived = srt.CashReceived
                # BankAmount = srt.BankAmount
                GrandTotal = srt.GrandTotal
                # CashAmount = srt.CashAmount
                Balance = srt.Balance
                TotalTax = srt.TotalTax
                BillDiscAmt = srt.BillDiscAmt

                VoucherType = "PR"

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    Credit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    Credit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                if float(TotalTax) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "55"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=TotalTax,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=TotalTax,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(BillDiscAmt) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "74"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=BillDiscAmt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=BillDiscAmt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "78"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerID = "78"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

        print("salesReturn==============================================================salesReturn")
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            salesRet_inst = SalesReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            for slst in salesRet_inst:
                VoucherType = "SR"
                SalesReturnMasterID = slst.SalesReturnMasterID
                VoucherNo = slst.VoucherNo
                VoucherDate = slst.VoucherDate
                SalesAccount = slst.SalesAccount
                TotalGrossAmt = slst.TotalGrossAmt
                IsActive = slst.IsActive
                Action = slst.Action
                CreatedUserID = slst.CreatedUserID
                today = slst.CreatedDate
                TaxType = slst.TaxType
                VATAmount = slst.VATAmount
                SGSTAmount = slst.SGSTAmount
                CGSTAmount = slst.CGSTAmount
                IGSTAmount = slst.IGSTAmount
                TAX1Amount = slst.TAX1Amount
                TAX2Amount = slst.TAX2Amount
                TAX3Amount = slst.TAX3Amount
                TotalDiscount = slst.TotalDiscount
                RoundOff = slst.RoundOff
                LedgerID = slst.LedgerID
                # CashReceived = slst.CashReceived
                # BankAmount = slst.BankAmount
                GrandTotal = slst.GrandTotal
                # CashAmount = slst.CashAmount
                Balance = slst.Balance
                TotalTax = slst.TotalTax
                BillDiscAmt = slst.BillDiscAmt


                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    Debit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    Debit=TotalGrossAmt,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                if float(TotalTax) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "55"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=TotalTax,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=TotalTax,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(BillDiscAmt) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "74"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=BillDiscAmt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Credit=BillDiscAmt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerID = "78"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerID = "78"

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
    print("------------------------->.................>>>>>>>>>>>>>>>>>>>>>......suucess")

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
