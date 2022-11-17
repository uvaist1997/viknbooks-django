from brands.models import LedgerPosting, LedgerPosting_Log, AccountLedger, AccountGroup, StockRate, StockPosting, Product, FinancialYear, PriceList,\
    CompanySettings, Parties, PaymentMaster, ReceiptMaster, SalesMaster, PurchaseMaster, SalesReturnMaster, PurchaseReturnMaster, SalesMaster_Log,\
    PurchaseMaster_Log, SalesReturnMaster_Log, PurchaseReturnMaster_Log, PaymentMaster_Log, ReceiptMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.ledgerPosting.serializers import LedgerPostingSerializer, LedgerPostingRestSerializer, ListSerializerforTrialBalance,\
    TrialBalanceSerializer, ListSerializerforLedgerReport, LedgerReportAllSerializer, LedgerReportGroupSerializer, ListSerializerforProfitAndLoss, ProfitAndLossSerializer,\
    BalanceSheetSerializer, LedgerReportLedgerWiseSerializer, StockReportSerializer, LedgerReportSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.stockPostings.serializers import StockPostingRestSerializer, StockValueAllSerializer, StockValueSingleSerializer
from api.v8.ledgerPosting.functions import DayBook_excel_data, export_to_excel_DayBook, export_to_excel_outStandingReport, generate_serializer_errors, outStandingReport_excel_data, profitAndLoss_balancing
from rest_framework import status
from api.v8.sales.serializers import ListSerializerforReport, ListSerializerforStockReport, ListSerializerforStockValueReport, ListSerializerforStockValueReportSingle
from api.v8.ledgerPosting.functions import balanceSheet_balancing, balanceSheet_excel_data, export_to_excel_balanceSheet, profitAndLoss_excel_data, export_to_excel_profitAndLoss, get_auto_id, convertOrderdDict, get_VoucherName, ledgerReport_excel_data, export_to_excel_ledgerReport, trialBalance_excel_data, export_to_excel_trialBalance
import datetime
from django.db.models import Sum
from django.shortcuts import render
from main.functions import get_company
from api.v8.companySettings.serializers import CompanySettingsRestSerializer
from django.db.models import F
from itertools import chain, groupby
from operator import itemgetter
from pprint import pprint
import collections
import functools
import operator
from collections import defaultdict
from django.http import HttpResponse
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_ledgerPosting(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = LedgerPostingSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        Date = serialized.data['Date']
        VoucherNo = serialized.data['VoucherNo']
        VoucherMasterID = serialized.data['VoucherMasterID']
        VoucherType = serialized.data['VoucherType']
        LedgerID = serialized.data['LedgerID']
        Debit = serialized.data['Debit']
        Credit = serialized.data['Credit']
        IsActive = serialized.data['IsActive']

        Action = "A"

        LedgerPostingID = get_auto_id(LedgerPosting, BranchID, CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherNo=VoucherNo,
            VoucherMasterID=VoucherMasterID,
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
            Date=Date,
            VoucherNo=VoucherNo,
            VoucherMasterID=VoucherMasterID,
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

        data = {"LedgerPostingID": LedgerPostingID}
        data.update(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_ledgerPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = LedgerPostingSerializer(data=request.data)
    instance = None
    if LedgerPosting.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LedgerPosting.objects.get(pk=pk, CompanyID=CompanyID)

        LedgerPostingID = instance.LedgerPostingID
        BranchID = instance.BranchID

    if instance:
        if serialized.is_valid():
            Date = serialized.data['Date']
            VoucherNo = serialized.data['VoucherNo']
            VoucherMasterID = serialized.data['VoucherMasterID']
            VoucherType = serialized.data['VoucherType']
            LedgerID = serialized.data['LedgerID']
            Debit = serialized.data['Debit']
            Credit = serialized.data['Credit']
            IsActive = serialized.data['IsActive']

            Action = "M"

            instance.Date = Date
            instance.VoucherMasterID = VoucherMasterID
            instance.VoucherType = VoucherType
            instance.LedgerID = LedgerID
            instance.Debit = Debit
            instance.Credit = Credit
            instance.IsActive = IsActive
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherNo=VoucherNo,
                VoucherMasterID=VoucherMasterID,
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

            data = {"LedgerPostingID": LedgerPostingID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Ledger Posting Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def ledgerPostings(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            instances = LedgerPosting.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)

            serialized = LedgerPostingRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Ledger Posting Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def ledgerPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if LedgerPosting.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LedgerPosting.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LedgerPostingRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "LedgerPosting Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_ledgerPosting(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if LedgerPosting.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LedgerPosting.objects.get(pk=pk, CompanyID=CompanyID)
        LedgerPostingID = instance.LedgerPostingID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherMasterID = instance.VoucherMasterID
        VoucherType = instance.VoucherType
        VoucherNo = instance.VoucherNo
        LedgerID = instance.LedgerID
        Debit = instance.Debit
        Credit = instance.Credit
        IsActive = instance.IsActive
        Action = "D"

        instance.delete()

        LedgerPosting_Log.objects.create(
            TransactionID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherNo=VoucherNo,
            VoucherMasterID=VoucherMasterID,
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
        response_data = {
            "StatusCode": 6000,
            "message": "Ledger Posting Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Ledger Posting Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def trialBalance(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforTrialBalance(data=request.data)

    company_instance = CompanySettings.objects.get(pk=CompanyID.id)
    company_serialized = CompanySettingsRestSerializer(
        company_instance, context={"request": request})

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        ToDate = serialized1.data['ToDate']

        if LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            TotalDebit = 0
            TotalCredit = 0
            TotalDebitForLOB = 0
            TotalCreditForLOB = 0
            DifferenceForLOB = 0
            test_arr = []

            instances = LedgerPosting.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Date__lte=ToDate)

            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])
            for instance in instances:
                TotalDebit += instance.Debit
                TotalCredit += instance.Credit

            if instances:
                account_ledger = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID__in=test_arr)
                serialized = TrialBalanceSerializer(account_ledger, many=True, context={
                                                    "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)
                new_jsnDatas = convertOrderdDict(orderdDict)

                # TotalAvgValueOpening = 0
                # FromDate = FinancialYear.objects.get(
                #     CompanyID=CompanyID, IsClosed=False).FromDate
                # # opening stock till financial year
                # if StockPosting.objects.filter(Date__lt=FromDate, CompanyID=CompanyID).exists():
                #     stock_instance_CS = StockPosting.objects.filter(
                #         Date__lte=FromDate, CompanyID=CompanyID)
                #     QtyInTot = 0
                #     QtyOutTot = 0
                #     for si in stock_instance_CS:

                #         QtyInTot += (float(si.QtyIn) * float(si.Rate))
                #         QtyOutTot += (float(si.QtyOut) * float(si.Rate))

                #     TotalAvgValueOpening = float(QtyInTot) - float(QtyOutTot)

                # # opening stock after financial year
                # if StockPosting.objects.filter(Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                #     stock_instance_CS = StockPosting.objects.filter(
                #         Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS")
                #     QtyInTot = 0
                #     QtyOutTot = 0
                #     for si in stock_instance_CS:

                #         QtyInTot += (float(si.QtyIn) * float(si.Rate))
                #         QtyOutTot += (float(si.QtyOut) * float(si.Rate))

                #     TotalAvgValueOpening += (float(QtyInTot) -
                #                              float(QtyOutTot))

                TotalAvgValueOpening = 0

                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                    product_instances_CS = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                    for pi in product_instances_CS:
                        ProductID = pi.ProductID

                        if StockPosting.objects.filter(ProductID=ProductID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                            stock_instance_CS = StockPosting.objects.filter(
                                ProductID=ProductID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS")
                            QtyInRate = 0
                            QtyOutTot = 0
                            QtyInTot = 0
                            for si in stock_instance_CS:
                                QtyInRate += (float(si.QtyIn) * float(si.Rate))
                                QtyInTot += float(si.QtyIn)
                                QtyOutTot += float(si.QtyOut)

                            stock = float(QtyInTot) - float(QtyOutTot)

                            AvgRate = 0
                            if QtyInTot > 0:
                                AvgRate = float(QtyInRate) / float(QtyInTot)

                            TotalAvgValueOpening += float(stock) * \
                                float(AvgRate)

                if TotalAvgValueOpening > 0:
                    OpeningStock = {
                        "LedgerName": "OpeningStock",
                        "LedgerID": "-",
                        "Debit": TotalAvgValueOpening,
                        "Credit": 0,
                        "VoucherType": "-",
                    }
                    jsnDatas.append(OpeningStock)
                    new_jsnDatas.append(OpeningStock)
                elif TotalAvgValueOpening < 0:
                    OpeningStock = {
                        "LedgerName": "OpeningStock",
                        "LedgerID": "-",
                        "Debit": 0,
                        "Credit": TotalAvgValueOpening,
                        "VoucherType": "-",
                    }
                    jsnDatas.append(OpeningStock)
                    new_jsnDatas.append(OpeningStock)

                for i in jsnDatas:
                    LedgerName = i['LedgerName']
                    LedgerID = i['LedgerID']
                    Debit = i['Debit']
                    Credit = i['Credit']
                    VoucherType = i['VoucherType']

                    # if VoucherType == 'LOB':
                    #     TotalDebitForLOB += Debit
                    #     TotalCreditForLOB += Credit

                    TotalDebitForLOB += Debit
                    TotalCreditForLOB += Credit

                is_DebitGreater = False
                is_CreditGreater = False
                Total = 0

                if TotalDebitForLOB > TotalCreditForLOB:
                    Total = TotalDebitForLOB
                    is_DebitGreater = True
                    difference = float(TotalDebitForLOB) - \
                        float(TotalCreditForLOB)

                elif TotalDebitForLOB < TotalCreditForLOB:
                    Total = TotalCreditForLOB
                    is_CreditGreater = True
                    difference = float(TotalCreditForLOB) - \
                        float(TotalDebitForLOB)
                else:
                    difference = 0
                    Total = TotalDebitForLOB

                # Total = 0
                # if TotalDebit > TotalCredit:
                #     Total = float(Total) + float(TotalDebit)
                # elif TotalDebit < TotalCredit:
                #     Total = float(Total) + float(TotalCredit)
                # else:
                #     Total = float(Total) + float(TotalDebit)

                # New style Page function Start
                deb = ""
                crd = ""
                if difference > 0:
                    deb = difference
                    crd = ""
                elif difference < 0:
                    deb = ""
                    crd = difference
                if not difference == 0:
                    dic = {
                        "LedgerName": "Opening Balance Difference",
                        "LedgerID": "-",
                        "Debit": deb,
                        "Credit": crd,
                        "VoucherType": "-",
                    }
                    new_jsnDatas.append(dic)
                # Adding Total to new_jsnDatas array
                dic = {
                    "LedgerName": "Total",
                    "LedgerID": "-",
                    "Debit": Total,
                    "Credit": Total,
                    "VoucherType": "-",
                }
                new_jsnDatas.append(dic)
                # New style Page function End

                response_data = {
                    "StatusCode": 6000,
                    "data": jsnDatas,
                    "new_data": new_jsnDatas,
                    "TotalDebit": TotalDebit,
                    "TotalCredit": TotalCredit,
                    "Total": Total,
                    "TotalDebitForLOB": TotalDebitForLOB,
                    "TotalCreditForLOB": TotalCreditForLOB,
                    "difference": difference,
                    "is_DebitGreater": is_DebitGreater,
                    "is_CreditGreater": is_CreditGreater,
                    "OpeningStock": TotalAvgValueOpening,
                    "company_data": company_serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Account Ledger Not Found Till this date!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide a date!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def ledgerReport(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializerforLedgerReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']
        ID = serialized1.data['ID']
        value = serialized1.data['value']

        try:
            ManualOpeningBalance = data['ManualOpeningBalance']
        except:
            ManualOpeningBalance = ""

        print("><-------------------------------------------><")
        print(ManualOpeningBalance)

        if LedgerPosting.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            test_arr = []
            if ID == 0:
                instances = LedgerPosting.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID, Date__lte=ToDate).order_by('Date', 'LedgerPostingID')
                ledger_ids = instances.values_list('LedgerID')
                for ledger_id in ledger_ids:
                    if ledger_id[0] not in test_arr:
                        test_arr.append(ledger_id[0])

                account_ledger = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID__in=test_arr)
                serialized = LedgerReportAllSerializer(account_ledger, many=True, context={
                                                       "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    Debit = i['Debit']
                    Credit = i['Credit']
                    Balance = float(i['Balance'])

                    # Balance = float(Debit) - float(Credit)

                    i['Balance'] = round(Balance, PriceRounding)
                if jsnDatas:
                    response_data = {
                        "StatusCode": 6000,
                        "data": jsnDatas,
                        "new_data": jsnDatas,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "No Datas with this Ledger during this date!"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            elif ID == 1:
                instances = LedgerPosting.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID).order_by('Date', 'LedgerPostingID')
                virtual_array = []
                last_data = []
                new_last_data = []
                ob_array = []
                Balance = 0
                if ManualOpeningBalance:
                    Balance = ManualOpeningBalance
                OpeningBalance = 0
                if instances.filter(CompanyID=CompanyID, LedgerID=value).exists():
                    if ManualOpeningBalance:
                        instances = instances.filter(
                            CompanyID=CompanyID, LedgerID=value, Date__gte=FromDate, Date__lte=ToDate).order_by('Date', 'LedgerPostingID')
                    else:
                        instances = instances.filter(
                            CompanyID=CompanyID, LedgerID=value).order_by('Date', 'LedgerPostingID')

                    serialized = LedgerReportLedgerWiseSerializer(instances, many=True, context={
                                                                  "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                    orderdDict = serialized.data
                    jsnDatas = convertOrderdDict(orderdDict)

                    for i in jsnDatas:
                        Unq_id = i['Unq_id']
                        Debit = i['Debit']
                        Credit = i['Credit']
                        LedgerID = i['LedgerID']
                        LedgerName = i['LedgerName']
                        RelatedLedgerName = i['RelatedLedgerName']
                        VoucherType = i['VoucherType']
                        VoucherNo = i['VoucherNo']
                        Date = i['Date']
                        Balance = (float(Balance) + float(Debit)) - \
                            float(Credit)

                        i['Balance'] = round(Balance, PriceRounding)
                        Debit = float(Debit)
                        Credit = float(Credit)

                        virtual_dictionary = {"Unq_id": Unq_id, "Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding), "LedgerID": LedgerID, "LedgerName": LedgerName,
                                              "RelatedLedgerName": RelatedLedgerName, "VoucherType": VoucherType, "VoucherNo": VoucherNo, "Date": Date, "Balance": round(Balance, PriceRounding)}

                        virtual_array.append(virtual_dictionary)

                    for i in virtual_array:
                        date = i["Date"]
                        if FromDate > date:
                            ob_array.append(i)
                        if FromDate <= date and ToDate >= date:
                            last_data.append(i)
                            # New Design Array START
                            dic = {
                                "VoucherNo": i['VoucherNo'],
                                "Date": i['Date'],
                                "VoucherType": i['VoucherType'],
                                "Particulars": i['RelatedLedgerName'],
                                "Debit": i['Debit'],
                                "Credit": i['Credit'],
                                "Balance": i['Balance'],
                            }
                            new_last_data.append(dic)
                            # New Design Function END

                    if ManualOpeningBalance:
                        OpeningBalance = ManualOpeningBalance
                    else:
                        if ob_array:
                            last_dict = ob_array[-1]
                            OpeningBalance = last_dict['Balance']
                    # if last_data:
                    TotalDebit = 0
                    TotalCredit = 0
                    TotalBalance = 0
                    for data in last_data:
                        TotalDebit += data['Debit']
                        TotalCredit += data['Credit']
                        # TotalBalance += data['Balance']

                    if float(OpeningBalance) > 0:
                        TotalDebit = float(TotalDebit) + float(OpeningBalance)
                    elif float(OpeningBalance) < 0:
                        TotalCredit = float(TotalCredit) + \
                            float(OpeningBalance)
                    TotalBalance = float(TotalDebit) - float(TotalCredit)
                    # Adding Opening Balance To new design array START
                    if int(OpeningBalance) < 0:
                        new_credit = OpeningBalance
                        new_debit = 0
                    else:
                        new_debit = OpeningBalance
                        new_credit = 0

                    dic = {
                        "VoucherNo": "-",
                        "Date": FromDate,
                        "VoucherType": "Opening Balance",
                        "Particulars": "-",
                        "Debit": new_debit,
                        "Credit": new_credit,
                        "Balance": OpeningBalance,
                    }
                    new_last_data.insert(0, dic)
                    # Adding Opening Balance To new design array END
                    # Adding Total To new design array START
                    dic = {
                        "VoucherNo": "-",
                        "Date": "-",
                        "VoucherType": "-",
                        "Particulars": "Total",
                        "Debit": round(TotalDebit, PriceRounding),
                        "Credit": round(TotalCredit, PriceRounding),
                        "Balance": round(TotalBalance, PriceRounding),
                    }
                    new_last_data.append(dic)
                    # Adding Total To new design array END
                    response_data = {
                        "StatusCode": 6000,
                        "data": last_data,
                        "new_data": new_last_data,
                        "OpeningBalance": OpeningBalance,
                        "TotalDebit": round(TotalDebit, PriceRounding),
                        "TotalCredit": round(TotalCredit, PriceRounding),
                        "TotalBalance": round(TotalBalance, PriceRounding),
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                    # else:
                    #     response_data = {
                    #         "StatusCode": 6001,
                    #         "message": "No Datas with this Ledger during this date!"
                    #     }
                    #     return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "No Datas with this Ledger!"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            elif ID == 2:
                instances = LedgerPosting.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID).order_by('Date', 'LedgerPostingID')
                virtual_array = []
                last_data = []
                new_last_data = []
                ob_array = []
                Balance = 0
                OpeningBalance = 0
                # instances = instances.filter(
                #     CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).order_by('Date')
                serialized = LedgerReportGroupSerializer(instances, many=True, context={
                                                         'value': value, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                filtered_array = []

                for i in jsnDatas:
                    Debit = i['Debit']
                    Credit = i['Credit']
                    LedgerName = i['LedgerName']
                    LedgerID = i['LedgerID']
                    GroupUnder = i['GroupUnder']
                    Date = i['Date']

                    # Balance = (float(Balance) + float(Debit)) - float(Credit)

                    i['Balance'] = round(Balance, PriceRounding)
                    Debit = float(Debit)
                    Credit = float(Credit)

                    if GroupUnder == True:
                        Balance = (float(Balance) + float(Debit)) - \
                            float(Credit)
                        filtered_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName, "Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding),
                                               "Balance": round(Balance, PriceRounding), "Date": Date, "GroupUnder": GroupUnder, }

                        filtered_array.append(filtered_dictionary)

                for i in filtered_array:
                    date = i["Date"]

                    if FromDate > date:
                        ob_array.append(i)
                    if FromDate <= date and ToDate >= date:
                        last_data.append(i)
                        # New Design Array START
                        dic = {
                            "LedgerName": i['LedgerName'],
                            "Debit": i['Debit'],
                            "Credit": i['Credit'],
                            "Balance": i['Balance'],
                        }
                        new_last_data.append(dic)
                        # New Design Function END

                if ob_array:
                    last_dict = ob_array[-1]
                    OpeningBalance = last_dict['Balance']

                # Adding Opening Balance To new design array START
                if int(OpeningBalance) < 0:
                    new_credit = OpeningBalance
                    new_debit = 0
                else:
                    new_debit = OpeningBalance
                    new_credit = 0

                dic = {
                    "LedgerName": "OpeningBalance",
                    "Debit": new_debit,
                    "Credit": new_credit,
                    "Balance": OpeningBalance,
                }
                new_last_data.insert(0, dic)
                # Adding Opening Balance To new design array END
                # if last_data:
                TotalDebit = 0
                TotalCredit = 0
                TotalBalance = 0
                for data in new_last_data:
                    TotalDebit += data['Debit']
                    TotalCredit += data['Credit']
                    # TotalBalance += data['Balance']
                TotalBalance = float(TotalDebit) - float(TotalCredit)
                # Adding Total To new design array START
                dic = {
                    "LedgerName": "Total",
                    "Debit": round(TotalDebit, PriceRounding),
                    "Credit": round(TotalCredit, PriceRounding),
                    "Balance": round(TotalBalance, PriceRounding),
                }
                new_last_data.append(dic)
                # Adding Total To new design array END
                response_data = {
                    "StatusCode": 6000,
                    "data": last_data,
                    "new_data": new_last_data,
                    "OpeningBalance": OpeningBalance,
                    "TotalDebit": round(TotalDebit, PriceRounding),
                    "TotalCredit": round(TotalCredit, PriceRounding),
                    "TotalBalance": round(TotalBalance, PriceRounding),
                }
                return Response(response_data, status=status.HTTP_200_OK)
                # else:
                #     response_data = {
                #         "StatusCode": 6001,
                #         "message": "No Datas under this group!"
                #     }
                #     return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Datas in this Branch!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']
        value = serialized1.data['value']
        print(value, "KAYARUNNUND................!1")
        ID = serialized1.data['ID']
        if not FromDate and not ToDate:
            response_data = {
                "StatusCode": 6001,
                "message": "please Select Dates!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
        if not value:

            if ID == 1:
                response_data = {
                    "StatusCode": 6001,
                    "message": "please Select Ledger!"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            elif ID == 2:
                response_data = {
                    "StatusCode": 6001,
                    "message": "please Select Group!"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(serialized1._errors)
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized1._errors)
            }
            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def profitAndLoss(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializerforProfitAndLoss(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():

            TotalCoast = 0
            TotalDirectExpense = 0
            TotalDirectIncome = 0
            TotalIndirectExpense = 0
            TotalInDirectIncome = 0
            test_arr = []
            instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])

            account_ledger = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID__in=test_arr)
            serialized = ProfitAndLossSerializer(
                account_ledger, many=True, context={"CompanyID": CompanyID})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            Direct_Expenses_Array = []
            Indirect_Expenses_Array = []
            Direct_Income_Array = []
            Indirect_Income_Array = []

            for i in jsnDatas:
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                GroupUnder = i['GroupUnder']
                Balance = i['Balance']

                if GroupUnder == 'Direct Expenses':

                    TotalDirectExpense += Balance
                    Direct_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                  "Balance": Balance, "GroupUnder": GroupUnder, }

                    Direct_Expenses_Array.append(Direct_Expenses_dictionary)
                elif GroupUnder == 'Indirect Expenses':
                    TotalIndirectExpense += Balance
                    Indirect_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                    "Balance": Balance, "GroupUnder": GroupUnder, }

                    Indirect_Expenses_Array.append(
                        Indirect_Expenses_dictionary)
                elif GroupUnder == 'Direct Income':
                    TotalDirectIncome += Balance
                    Direct_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                "Balance": Balance, "GroupUnder": GroupUnder, }

                    Direct_Income_Array.append(Direct_Income_dictionary)

                elif GroupUnder == 'Indirect Income':
                    TotalInDirectIncome += Balance
                    Indirect_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                  "Balance": Balance, "GroupUnder": GroupUnder, }

                    Indirect_Income_Array.append(Indirect_Income_dictionary)

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stock_instances = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                for stock_instance in stock_instances:
                    TotalCoast += stock_instance.Cost

            is_DirectexpenseGreater = False
            is_IndirectexpenseGreater = False
            is_DirectincomeGreater = False
            is_IndirectincomeGreater = False

            TotalDirectIncomeWithStock = float(
                TotalCoast) + float(TotalDirectIncome)

            if TotalDirectIncomeWithStock > TotalDirectExpense:
                is_DirectincomeGreater = True
                TotalDirect = TotalDirectIncomeWithStock
                Direct_difference = float(
                    TotalDirectIncomeWithStock) - float(TotalDirectExpense)
            elif TotalDirectIncomeWithStock < TotalDirectExpense:
                is_DirectexpenseGreater = True
                TotalDirect = TotalDirectExpense
                Direct_difference = float(
                    TotalDirectExpense) - float(TotalDirectIncomeWithStock)
            else:
                TotalDirect = 0
                Direct_difference = 0

            if TotalIndirectExpense > TotalInDirectIncome:
                is_IndirectexpenseGreater = True
                TotalIndirect = TotalIndirectExpense
                Indirectdifference = float(
                    TotalIndirectExpense) - float(TotalInDirectIncome)
            elif TotalIndirectExpense < TotalInDirectIncome:
                is_IndirectincomeGreater = True
                TotalIndirect = TotalInDirectIncome
                Indirectdifference = float(
                    TotalInDirectIncome) - float(TotalIndirectExpense)
            else:
                Indirectdifference = 0
                TotalIndirect = 0

            response_data = {
                "StatusCode": 6000,
                "DirectExpensesData": Direct_Expenses_Array,
                "InDirectExpensesData": Indirect_Expenses_Array,
                "DirectIncomeData": Direct_Income_Array,
                "IndirectIncomeData": Indirect_Income_Array,
                "TotalCoast": TotalCoast,
                "TotalDirect": TotalDirect,
                "TotalIndirect": TotalIndirect,
                # "TotalDirectIncomeWithStock" : TotalDirectIncomeWithStock,
                # "TotalDirectExpense" : TotalDirectExpense,
                # "TotalIndirectExpense" : TotalIndirectExpense,
                # "TotalInDirectIncome" : TotalInDirectIncome,
                "DirectIncomeGreater": is_DirectincomeGreater,
                "DirectExpenseGreater": is_DirectexpenseGreater,
                "IndirectExpenseGreater": is_IndirectexpenseGreater,
                "IndirectIncomeGreater": is_IndirectincomeGreater,
                "Direct_difference": Direct_difference,
                "Indirectdifference": Indirectdifference
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Datas During this Time Periods!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


# ------------------------------------
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def balanceSheet(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializerforProfitAndLoss(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():

            TotalCoast = 0
            TotalAssets = 0
            TotalLiabilitis = 0
            test_arr = []
            instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])
            if instances:
                account_ledger = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID__in=test_arr)
                serialized = BalanceSheetSerializer(
                    account_ledger, many=True, context={"CompanyID": CompanyID})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                Assets_Array = []
                Liabilitis_Array = []

                for i in jsnDatas:
                    LedgerName = i['LedgerName']
                    LedgerID = i['LedgerID']
                    GroupUnder = i['GroupUnder']
                    Balance = i['Balance']

                    if GroupUnder == 'Assets':
                        TotalAssets += Balance
                        Assets_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                             "Balance": Balance, "GroupUnder": GroupUnder, }

                        Assets_Array.append(Assets_dictionary)
                    elif GroupUnder == 'Liabilitis':
                        TotalLiabilitis += Balance
                        Liabilitis_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                 "Balance": Balance, "GroupUnder": GroupUnder, }

                        Liabilitis_Array.append(Liabilitis_dictionary)

                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                    stock_instances = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                    for stock_instance in stock_instances:
                        TotalCoast += stock_instance.Cost

            is_AssetsGreater = False
            is_LiabilitisGreater = False
            Total = 0
            if TotalAssets > TotalLiabilitis:
                is_AssetsGreater = True
                difference = float(TotalAssets) - float(TotalLiabilitis)
                Total = TotalAssets
            elif TotalAssets < TotalLiabilitis:
                is_LiabilitisGreater = True
                difference = float(TotalLiabilitis) - float(TotalAssets)
                Total = TotalLiabilitis
            else:
                difference = 0
                Total = TotalAssets

            response_data = {
                "StatusCode": 6000,
                "AssetsData": Assets_Array,
                "LiabilitisData": Liabilitis_Array,
                "TotalAssets": TotalAssets,
                "TotalLiabilitis": TotalLiabilitis,
                "Total": Total,
                "difference": difference,
                "is_AssetsGreater": is_AssetsGreater,
                "is_LiabilitisGreater": is_LiabilitisGreater,
                "TotalCoast": TotalCoast
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Datas During this Time Periods!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def trialBalance_webView(request, pk):
    # LedgerID = request.GET.get('LedgerID')
    ToDate = request.GET.get('ToDate')
    test_arr = []
    TotalDebit = 0
    TotalCredit = 0
    instances = LedgerPosting.objects.filter(
        CompanyID=CompanyID, BranchID=pk, Date__lte=ToDate)
    for i in instances:
        TotalDebit += i.Debit
        TotalCredit += i.Credit
    ledger_ids = instances.values_list('LedgerID')
    for ledger_id in ledger_ids:
        if ledger_id[0] not in test_arr:
            test_arr.append(ledger_id[0])

    account_ledgers = AccountLedger.objects.filter(
        CompanyID=CompanyID, LedgerID__in=test_arr).order_by('id')

    context = {
        "title": "LEDGER REPORT",
        "instances": instances,
        "account_ledgers": account_ledgers,
        "ToDate": ToDate,
        "TotalDebit": TotalDebit,
        "TotalCredit": TotalCredit,
    }
    return render(request, 'trial_balance.html', context)


@api_view(['GET'])
def ledgerReport_webView(request, pk):
    # LedgerID = request.GET.get('LedgerID')
    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')
    Ledger = request.GET.get('Ledger')
    test_arr = []
    TotalDebit = 0
    TotalCredit = 0
    instances = LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=pk,)

    context = {
        "title": "LEDGER REPORT",
        "instances": instances,
        "FromDate": FromDate,
        "ToDate": ToDate,
        "TotalDebit": TotalDebit,
        "TotalCredit": TotalCredit,
    }
    return render(request, 'ledger_report.html', context)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def report_stock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforStockReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        WareHouseID = serialized1.data['WareHouseID']

        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID).exists():
            instances = StockRate.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID)

            serialized = StockReportSerializer(instances, many=True, context={
                                               "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No data under this warehouse!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def report_stockValue(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforStockValueReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        WareHouseID = serialized1.data['WareHouseID']
        ToDate = serialized1.data['ToDate']

        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate).exists():

            test_arr = []
            instances = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate)
            product_ids = instances.values_list('ProductID')
            for p_id in product_ids:
                if p_id[0] not in test_arr:
                    test_arr.append(p_id[0])

            product_instances = Product.objects.filter(
                CompanyID=CompanyID, ProductID__in=test_arr, BranchID=BranchID)

            serialized = StockValueAllSerializer(
                product_instances, many=True, context={"CompanyID": CompanyID})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No data under this Date Range!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def report_stockValue_SingleProduct(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforStockValueReportSingle(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        WareHouseID = serialized1.data['WareHouseID']
        ProductID = serialized1.data['ProductID']
        ToDate = serialized1.data['ToDate']
        FromDate = serialized1.data['FromDate']

        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate, ProductID=ProductID).exists():
            instances = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate, ProductID=ProductID)

            totalQtyIn = 0
            totalQtyOut = 0
            for i in instances:
                totalQtyIn += i.QtyIn
                totalQtyOut += i.QtyOut
            Stock = totalQtyIn - totalQtyOut

            serialized = StockValueSingleSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "Stock": Stock
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No data under this Date Range!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def profitAndLoss_web(request):
    data = request.data
    CompanyID = data['CompanyID']
    try:
        key = data['key']
    except:
        key = ""
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = int(PriceRounding)
    serialized1 = ListSerializerforProfitAndLoss(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        try:
            ManualOpeningStock = data['ManualOpeningStock']
        except:
            ManualOpeningStock = ""

        try:
            ManualClosingStock = data['ManualClosingStock']
        except:
            ManualClosingStock = ""

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            TotalCoast = 0
            TotalDirectExpense = 0
            TotalDirectIncome = 0
            TotalIndirectExpense = 0
            TotalInDirectIncome = 0
            test_arr = []
            instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])

            account_ledger = AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID__in=test_arr)
            serialized = ProfitAndLossSerializer(
                account_ledger, many=True, context={"CompanyID": CompanyID, "FromDate": FromDate, "ToDate": ToDate})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            Direct_Expenses_Array = []
            Indirect_Expenses_Array = []
            Direct_Income_Array = []
            Indirect_Income_Array = []

            dirExArr = []

            name_exist_dirExp = {}
            name_exist_detailed_dirExp = {}
            dic_exGrp_dirExp = {}
            final_direct_expence_arr = []

            name_exist_indirExp = {}
            name_exist_detailed_indirExp = {}
            dic_exGrp_indirExp = {}
            final_indirect_expence_arr = []

            name_exist_dirInc = {}
            name_exist_detailed_dirInc = {}
            dic_exGrp_dirInc = {}
            final_direct_income_arr = []

            name_exist_indirInc = {}
            name_exist_detailed_indirInc = {}
            dic_exGrp_indirInc = {}
            final_indirect_income_arr = []

            TotalAvgValueOpening = 0
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                product_instances_OS = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")
                voucherTypes = ["PI", "OS", "ES"]
                product_ids = product_instances_OS.values_list('ProductID')
                # for pi in product_instances_OS:
                #     ProductID = pi.ProductID
                # # opening stock before financial year

                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                    product_instances_CS = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                    # for pi in product_instances_CS:
                    #     ProductID = pi.ProductID
                    product_ids = product_instances_CS.values_list('ProductID')
                    # new start
                    if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes).exists():
                        stock_instances_new = StockPosting.objects.filter(
                            ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes, QtyIn__gt=0)

                        qurried_instances = stock_instances_new.values('ProductID').annotate(
                            sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                        TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID).values(
                            'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                        result_list = sorted(
                            chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                        names = [i.get('ProductID') for i in result_list]
                        points = [i.get('sum_in_rate') for i in result_list]
                        # pprint(points)

                        content_list = {}
                        for (name, score) in zip(names, points):
                            if name in content_list.keys():
                                # if the value is already in list, add current score to the sum
                                content_list[name] *= score
                            else:
                                # if the value is not yet in list, create an entry
                                content_list[name] = score

                        values = content_list.values()
                        TotalAvgValueOpening = sum(values)

                # if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes).exists():
                #     stock_instances_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID, VoucherType__in=voucherTypes, QtyIn__gt=0)
                #     TotalRateIn_new_os = stock_instances_new_os.aggregate(
                #         total_sum=Sum(F('QtyIn') * F('Rate')))
                #     sum_QtyIn_os = stock_instances_new_os.aggregate(
                #         Sum('QtyIn'))
                #     sum_QtyIn_os = sum_QtyIn_os['QtyIn__sum']
                #     TotalQtyIn_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID).aggregate(Sum('QtyIn'))
                #     TotalQtyOut_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__lt=FromDate, CompanyID=CompanyID).aggregate(Sum('QtyOut'))
                #     TotalQtyIn_new_os = TotalQtyIn_new_os['QtyIn__sum']
                #     TotalQtyOut_new_os = TotalQtyOut_new_os['QtyOut__sum']
                #     stock_new_os = float(
                #         TotalQtyIn_new_os) - float(TotalQtyOut_new_os)

                #     AvgRate_new = 0
                #     if float(sum_QtyIn_os) > 0:
                #         AvgRate_new = float(
                #             TotalRateIn_new_os['total_sum']) / float(sum_QtyIn_os)
                #     TotalAvgValueOpening += (float(stock_new_os)
                #                              * float(AvgRate_new))

                # # opening stock with in financial year
                # if StockPosting.objects.filter(ProductID=ProductID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                #     stock_instance_OS = StockPosting.objects.filter(
                #         ProductID=ProductID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS")
                #     QtyInRate = 0
                #     QtyOutTot = 0
                #     QtyInTot = 0
                #     for si in stock_instance_OS:
                #         QtyInRate += (float(si.QtyIn) * float(si.Rate))
                #         QtyInTot += float(si.QtyIn)
                #         QtyOutTot += float(si.QtyOut)

                #     stock = float(QtyInTot) - float(QtyOutTot)

                #     AvgRate = 0
                #     if QtyInTot > 0:
                #         AvgRate = float(QtyInRate) / float(QtyInTot)

                #     TotalAvgValueOpening += float(stock) * float(AvgRate)

                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                    product_instances_CS = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                    # for pi in product_instances_CS:
                    #     ProductID = pi.ProductID
                    product_ids = product_instances_CS.values_list('ProductID')
                    # new start
                    if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS").exists():
                        stock_instances_new = StockPosting.objects.filter(
                            ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID, VoucherType="OS", QtyIn__gt=0)

                        print(stock_instances_new)
                        qurried_instances = stock_instances_new.values('ProductID').annotate(
                            sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                        TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID).values(
                            'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                        result_list = sorted(
                            chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                        names = [i.get('ProductID') for i in result_list]
                        points = [i.get('sum_in_rate') for i in result_list]
                        # pprint(points)

                        content_list = {}
                        for (name, score) in zip(names, points):
                            if name in content_list.keys():
                                # if the value is already in list, add current score to the sum
                                content_list[name] *= score
                            else:
                                # if the value is not yet in list, create an entry
                                content_list[name] = score

                        values = content_list.values()
                        TotalAvgValueOpening += sum(values)

                # if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, CompanyID=CompanyID, VoucherType="OS").exists():
                #     stock_instances_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, CompanyID=CompanyID, VoucherType="OS", QtyIn__gt=0)
                #     TotalRateIn_new_os = stock_instances_new_os.aggregate(
                #         total_sum=Sum(F('QtyIn') * F('Rate')))
                #     sum_QtyIn_os = stock_instances_new_os.aggregate(
                #         Sum('QtyIn'))
                #     sum_QtyIn_os = sum_QtyIn_os['QtyIn__sum']
                #     TotalQtyIn_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, CompanyID=CompanyID).aggregate(Sum('QtyIn'))
                #     TotalQtyOut_new_os = StockPosting.objects.filter(
                #         ProductID__in=product_ids, BranchID=BranchID, Date__gte=FromDate, CompanyID=CompanyID).aggregate(Sum('QtyOut'))
                #     TotalQtyIn_new_os = TotalQtyIn_new_os['QtyIn__sum']
                #     TotalQtyOut_new_os = TotalQtyOut_new_os['QtyOut__sum']
                #     stock_new_os = float(
                #         TotalQtyIn_new_os) - float(TotalQtyOut_new_os)

                #     AvgRate_new = 0
                #     if float(sum_QtyIn_os) > 0:
                #         AvgRate_new = float(
                #             TotalRateIn_new_os['total_sum']) / float(sum_QtyIn_os)
                #     TotalAvgValueOpening += (float(stock_new_os)
                #                              * float(AvgRate_new))

                # opening_stock_dic_dirEx = {}
            if ManualOpeningStock:
                TotalAvgValueOpening = float(ManualOpeningStock)
            name_exist_dirExp['Opening Stock'] = {
                # 'GroupName' : "Opening Stock",
                'Balance': float(TotalAvgValueOpening)
            }

            # opening stock end
            # closing stock start
            TotalAvgValueClosing = 0

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem").exists():
                product_instances_CS = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, InventoryType="StockItem")

                # for pi in product_instances_CS:
                #     ProductID = pi.ProductID
                product_ids = product_instances_CS.values_list('ProductID')
                # new start
                if StockPosting.objects.filter(ProductID__in=product_ids, BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType__in=voucherTypes).exists():
                    stock_instances_new = StockPosting.objects.filter(
                        ProductID__in=product_ids, BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID, VoucherType__in=voucherTypes, QtyIn__gt=0)

                    qurried_instances = stock_instances_new.values('ProductID').annotate(
                        sum_in_rate=Sum(F('QtyIn') * F('Rate')) / Sum('QtyIn')).order_by('ProductID')
                    TotalQty_new = StockPosting.objects.filter(BranchID=BranchID, Date__lte=ToDate, CompanyID=CompanyID).values(
                        'ProductID').annotate(sum_in_rate=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
                    result_list = sorted(
                        chain(qurried_instances, TotalQty_new), key=itemgetter('ProductID'))

                    names = [i.get('ProductID') for i in result_list]
                    points = [i.get('sum_in_rate') for i in result_list]
                    # pprint(points)

                    content_list = {}
                    for (name, score) in zip(names, points):
                        if name in content_list.keys():
                            # if the value is already in list, add current score to the sum
                            content_list[name] *= score
                        else:
                            # if the value is not yet in list, create an entry
                            content_list[name] = score

                    values = content_list.values()
                    TotalAvgValueClosing = sum(values)

            if ManualClosingStock:
                TotalAvgValueClosing = float(ManualClosingStock)
            # closing stock data for consolidated ends here
            test_dicT = {}

            for i in jsnDatas:
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                GroupUnder = i['GroupUnder']
                Balance = i['Balance']
                if GroupUnder == 'Direct Expenses':
                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                    # for consolidated start
                    dir_exp_Tot_Credit = 0
                    dir_exp_Tot_Debit = 0
                    for lpi in ledgerpost_ins:
                        dir_exp_Tot_Debit = + float(lpi.Debit)
                        dir_exp_Tot_Credit = + float(lpi.Credit)
                        dir_exp_balance = float(
                            dir_exp_Tot_Debit) - float(dir_exp_Tot_Credit)

                        dic_exGrp_dirExp = {"GroupName": str(
                            Group_name), "Balance": float(dir_exp_balance)}

                    if not Group_name in name_exist_dirExp:
                        # name_exist.append(Group_name)
                        dic_exGrp_dirExp = {
                            "Balance": float(Balance)
                        }
                        name_exist_dirExp[Group_name] = dic_exGrp_dirExp
                    else:
                        b = name_exist_dirExp[Group_name]["Balance"]
                        name_exist_dirExp[Group_name]["Balance"] = b + \
                            float(Balance)

                    # consolidated end
                    # detailed start
                    TotalDirectExpense += Balance
                    Direct_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                  "Balance": Balance, "GroupUnder": GroupUnder, }

                    if not Group_name in name_exist_detailed_dirExp:
                        name_exist_detailed_dirExp[Group_name] = []
                    name_exist_detailed_dirExp[Group_name].append(
                        Direct_Expenses_dictionary)

                    # dic = {
                    #     "group_name" : Group_name,
                    #     "ledgers" : Direct_Expenses_dictionary
                    # }
                    # if not Group_name in test_dicT:
                    #     test_dicT[Group_name] = []
                    # name_exist_detailed_dirExp[Group_name].append(Direct_Expenses_dictionary)
                elif GroupUnder == 'Indirect Expenses':

                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                    # for consolidated start
                    indir_exp_Tot_Credit = 0
                    indir_exp_Tot_Debit = 0
                    for lpi in ledgerpost_ins:
                        indir_exp_Tot_Debit = + lpi.Debit
                        dir_exp_Tot_Credit = + lpi.Credit
                        dir_exp_balance = indir_exp_Tot_Debit - indir_exp_Tot_Credit

                        dic_exGrp_indirExp = {"GroupName": str(
                            Group_name), "Balance": float(dir_exp_balance)}

                    if not Group_name in name_exist_indirExp:
                        # name_exist.append(Group_name)
                        dic_exGrp_indirExp = {
                            "Balance": float(Balance),
                        }
                        name_exist_indirExp[Group_name] = dic_exGrp_indirExp
                    else:
                        b = name_exist_indirExp[Group_name]["Balance"]
                        name_exist_indirExp[Group_name]["Balance"] = b + \
                            float(Balance)

                    # consolidated end
                    # detailed start
                    TotalIndirectExpense += Balance
                    Indirect_Expenses_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                    "Balance": Balance, "GroupUnder": GroupUnder, }

                    if not Group_name in name_exist_detailed_indirExp:
                        name_exist_detailed_indirExp[Group_name] = []
                    name_exist_detailed_indirExp[Group_name].append(
                        Indirect_Expenses_dictionary)

                elif GroupUnder == 'Direct Income':
                    if LedgerID == 86:
                        Balance = -(Balance)
                    if LedgerID == 85:
                        Balance = abs(Balance)
                    if LedgerID == 83:
                        Balance = abs(Balance)

                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                    # for consolidated start
                    dir_inc_Tot_Credit = 0
                    dir_inc_Tot_Debit = 0
                    for lpi in ledgerpost_ins:

                        dir_inc_Tot_Debit = + lpi.Debit
                        dir_inc_Tot_Credit = + lpi.Credit

                        dir_inc_balance = dir_inc_Tot_Debit - dir_inc_Tot_Credit

                        dir_inc_balance = dir_inc_balance

                        dic_exGrp_dirInc = {"GroupName": str(
                            Group_name), "Balance": float(dir_inc_balance)}
                    if not Group_name in name_exist_dirInc:
                        # name_exist.append(Group_name)
                        dic_exGrp_dirInc = {
                            "Balance": float(Balance),
                        }
                        name_exist_dirInc[Group_name] = dic_exGrp_dirInc
                    else:
                        b = name_exist_dirInc[Group_name]["Balance"]
                        name_exist_dirInc[Group_name]["Balance"] = b + \
                            float(Balance)

                    name_exist_dirInc['Closing Stock'] = {
                        # 'GroupName' : "Closing Stock",
                        'Balance': TotalAvgValueClosing
                    }

                    # consolidated end
                    # detailed start
                    TotalDirectIncome += Balance

                    Direct_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                "Balance": Balance, "GroupUnder": GroupUnder, }

                    if not Group_name in name_exist_detailed_dirInc:
                        name_exist_detailed_dirInc[Group_name] = []
                    name_exist_detailed_dirInc[Group_name].append(
                        Direct_Income_dictionary)

                    # TotalDirectIncome += Balance
                    # Direct_Income_dictionary = {"LedgerID" : LedgerID,"LedgerName" : LedgerName,
                    #                                 "Balance" : Balance,"GroupUnder" : GroupUnder, }

                    # Direct_Income_Array.append(Direct_Income_dictionary)

                elif GroupUnder == 'Indirect Income':

                    Group_Under = AccountLedger.objects.get(
                        BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                    Group_name = AccountGroup.objects.get(
                        AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                    ledgerpost_ins = LedgerPosting.objects.filter(
                        LedgerID=LedgerID, Date__range=(FromDate, ToDate), CompanyID=CompanyID)

                    # for consolidated start
                    indir_inc_Tot_Credit = 0
                    indir_inc_Tot_Debit = 0
                    for lpi in ledgerpost_ins:
                        indir_inc_Tot_Debit = + lpi.Debit
                        indir_inc_Tot_Credit = + lpi.Credit
                        indir_inc_balance = indir_inc_Tot_Debit - indir_inc_Tot_Credit

                        dic_exGrp_indirInc = {"GroupName": str(
                            Group_name), "Balance": float(abs(indir_inc_balance))}

                    if not Group_name in name_exist_indirInc:
                        dic_exGrp_indirInc = {
                            "Balance": float(Balance),
                        }
                        name_exist_indirInc[Group_name] = dic_exGrp_indirInc
                    else:
                        b = name_exist_indirInc[Group_name]["Balance"]
                        name_exist_indirInc[Group_name]["Balance"] = b + \
                            float(Balance)

                    TotalInDirectIncome += abs(Balance)
                    Indirect_Income_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                  "Balance": abs(Balance), "GroupUnder": GroupUnder, }

                    if not Group_name in name_exist_detailed_indirInc:
                        name_exist_detailed_indirInc[Group_name] = []
                    name_exist_detailed_indirInc[Group_name].append(
                        Indirect_Income_dictionary)

            final_direct_expence_arr.append(name_exist_dirExp)

            final_direct_income_arr.append(name_exist_dirInc)

            # final_direct_income_arr.append(closing_stock_dic_dirInc)

            final_indirect_expence_arr.append(name_exist_indirExp)

            final_indirect_income_arr.append(name_exist_indirInc)

            Direct_Expenses_Array.append(name_exist_detailed_dirExp)
            Indirect_Expenses_Array.append(name_exist_detailed_indirExp)
            Direct_Income_Array.append(name_exist_detailed_dirInc)
            Indirect_Income_Array.append(name_exist_detailed_indirInc)

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stock_instances = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                for stock_instance in stock_instances:
                    TotalCoast += stock_instance.Cost

            is_DirectexpenseGreater = False
            is_IndirectexpenseGreater = False
            is_DirectincomeGreater = False
            is_IndirectincomeGreater = False

            TotalDirectIncome = float(
                TotalDirectIncome) + float(TotalAvgValueClosing)
            # TotalDirectIncomeWithStock = float(TotalCoast) + float(TotalDirectIncome)
            TotalDirectExpense = float(
                TotalDirectExpense) + float(TotalAvgValueOpening)

            if TotalDirectIncome > TotalDirectExpense:
                is_DirectincomeGreater = True
                TotalDirect = TotalDirectIncome
                Direct_difference = float(
                    TotalDirectIncome) - float(TotalDirectExpense)
            elif TotalDirectExpense > TotalDirectIncome:
                is_DirectexpenseGreater = True
                TotalDirect = TotalDirectExpense
                Direct_difference = float(
                    TotalDirectExpense) - float(TotalDirectIncome)
            else:
                TotalDirect = TotalDirectExpense
                Direct_difference = 0

            if is_DirectincomeGreater == True:
                TotalInDirectIncome = TotalInDirectIncome + Direct_difference

            if is_DirectexpenseGreater == True:
                TotalIndirectExpense = TotalIndirectExpense + Direct_difference

            if TotalIndirectExpense > TotalInDirectIncome:
                is_IndirectexpenseGreater = True
                TotalIndirect = TotalIndirectExpense
                Indirectdifference = float(
                    TotalIndirectExpense) - float(TotalInDirectIncome)
            elif TotalIndirectExpense < TotalInDirectIncome:

                is_IndirectincomeGreater = True
                TotalIndirect = TotalInDirectIncome
                Indirectdifference = float(
                    TotalInDirectIncome) - float(TotalIndirectExpense)
            else:
                Indirectdifference = 0
                TotalIndirect = TotalIndirectExpense

            # direct expense final array starts here
            DirExPCons = []
            for i in final_direct_expence_arr[0]:

                myDic = {
                    'GroupName': i,
                    'Balance': float(round(final_direct_expence_arr[0][i]['Balance'], PriceRounding))
                }
                DirExPCons.append(myDic)

            # if is_DirectexpenseGreater == False:

            #     dirXG = {
            #         'GroupName' : 'Gross Profit',
            #         'Balance' : Direct_difference
            #     }
            #     DirExPCons.append(dirXG)
            # direct income final array starts here
            print("===========================")
            print(final_direct_income_arr[0])
            DirIncCons = []
            if final_direct_income_arr[0]:
                for i in final_direct_income_arr[0]:
                    print("----------------------")
                    print(i)
                    if i == "Closing Stock":
                        myDic = {
                            'GroupName': i,
                            'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                        }
                        DirIncCons.append(myDic)
                    else:
                        myDic = {
                            'GroupName': i,
                            'Balance': float(round(final_direct_income_arr[0][i]['Balance'], PriceRounding))
                        }
                        DirIncCons.append(myDic)
            else:
                myDic = {
                    'GroupName': "Closing Stock",
                    'Balance': float(round(TotalAvgValueClosing, PriceRounding))
                }
                DirIncCons.append(myDic)

            # if is_DirectincomeGreater == False:

            #     dirXIn = {
            #         'GroupName' : 'Gross Loss',
            #         'Balance' : float(round(Direct_difference,3))
            #     }
            #     DirIncCons.append(dirXIn)

            inDirIncCons = []
            inDirExpCons = []
            for i in final_indirect_income_arr[0]:
                myDic = {
                    'GroupName': i,
                    'Balance': float(round(abs(final_indirect_income_arr[0][i]['Balance']), PriceRounding))
                }
                inDirIncCons.append(myDic)

            for i in final_indirect_expence_arr[0]:
                myDic = {
                    'GroupName': i,
                    'Balance': float(round(final_indirect_expence_arr[0][i]['Balance'], PriceRounding))
                }
                inDirExpCons.append(myDic)

            # if is_IndirectexpenseGreater == False:
            #     dirXN = {
            #         'GroupName' : 'Net Profit',
            #         'Balance' : float(round(Indirectdifference,3))
            #     }
            #     inDirExpCons.append(dirXN)

            # if is_IndirectincomeGreater == False:
            #     dirXN = {
            #         'GroupName' : 'Net Loss',
            #         'Balance' : float(round(Indirectdifference,3))
            #     }
            #     inDirExpCons.append(dirXN)

            # TotalIndirect = TotalIndirect + Direct_difference

            # New Design Data Start
            profitAndLoss_final_data = profitAndLoss_balancing(key, DirExPCons, DirIncCons, inDirExpCons, inDirIncCons, is_DirectincomeGreater, is_DirectexpenseGreater, is_IndirectexpenseGreater, is_IndirectincomeGreater, Indirectdifference, Direct_difference, TotalDirect, TotalIndirect, Direct_Expenses_Array, Indirect_Expenses_Array, Direct_Income_Array, Indirect_Income_Array, TotalAvgValueOpening, TotalAvgValueClosing
                                                               )
            # New Design Data End

            response_data = {
                "StatusCode": 6000,
                "data": profitAndLoss_final_data,
                "DirectExpensesData": Direct_Expenses_Array,
                "InDirectExpensesData": Indirect_Expenses_Array,
                "DirectIncomeData": Direct_Income_Array,
                "IndirectIncomeData": Indirect_Income_Array,
                "TotalCoast": TotalCoast,
                "TotalDirect": TotalDirect,
                "TotalIndirect": TotalIndirect,
                "DirectIncomeGreater": is_DirectincomeGreater,
                "DirectExpenseGreater": is_DirectexpenseGreater,
                "IndirectExpenseGreater": is_IndirectexpenseGreater,
                "IndirectIncomeGreater": is_IndirectincomeGreater,
                "Direct_difference": Direct_difference,
                "Indirectdifference": Indirectdifference,
                "DirExPCons": DirExPCons,
                "inDirIncCons": inDirIncCons,
                "DirIncCons": DirIncCons,
                "inDirExpCons": inDirExpCons,
                "OpeningStock": TotalAvgValueOpening,
                "ClosingStock": TotalAvgValueClosing,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Datas During this Time Periods!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid Dates!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def balanceSheet_web(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializerforProfitAndLoss(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']
        PriceRounding = data['PriceRounding']

        # FromDate = FinancialYear.objects.get(CompanyID=CompanyID,IsClosed=False).FromDate

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():

            TotalCoast = 0
            TotalAssets = 0
            TotalLiabilitis = 0
            test_arr = []
            instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            ledger_ids = instances.values_list('LedgerID')
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr:
                    test_arr.append(ledger_id[0])
            if instances:
                account_ledger = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerID__in=test_arr)
                serialized = BalanceSheetSerializer(
                    account_ledger, many=True, context={"CompanyID": CompanyID, "FromDate": FromDate, "ToDate": ToDate})

                orderdDict = serialized.data
                jsnDatas = convertOrderdDict(orderdDict)

                Assets_Array = []
                Liabilitis_Array = []

                name_exist_liabilities = {}
                name_exist_detailed_liabilities = {}
                dic_exGrp_liabilities = {}
                final_liabilities_arr = []

                name_exist_asset = {}
                name_exist_detailed_asset = {}
                dic_exGrp_asset = {}
                final_asset_arr = []

                for i in jsnDatas:
                    LedgerName = i['LedgerName']
                    LedgerID = i['LedgerID']
                    GroupUnder = i['GroupUnder']
                    Balance = i['Balance']

                    if GroupUnder == 'Assets':
                        Group_Under = AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID)

                        # for consolidated start
                        asset_Tot_Credit = 0
                        asset_Tot_Debit = 0
                        for lpi in ledgerpost_ins:
                            asset_Tot_Debit = + float(lpi.Debit)
                            asset_Tot_Credit = + float(lpi.Credit)
                            asset_balance = float(
                                asset_Tot_Debit) - float(asset_Tot_Credit)

                            dic_exGrp_asset = {"GroupName": str(
                                Group_name), "Balance": float(asset_balance)}

                        if not Group_name in name_exist_asset:
                            # name_exist.append(Group_name)
                            dic_exGrp_asset = {
                                "Balance": float(Balance)
                            }
                            name_exist_asset[Group_name] = dic_exGrp_asset
                        else:
                            b = name_exist_asset[Group_name]["Balance"]
                            name_exist_asset[Group_name]["Balance"] = b + \
                                float(Balance)

                        TotalAssets += Balance
                        Assets_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                             "Balance": Balance, "GroupUnder": GroupUnder, }

                        # Assets_Array.append(Assets_dictionary)

                        if not Group_name in name_exist_detailed_asset:
                            name_exist_detailed_asset[Group_name] = []
                        name_exist_detailed_asset[Group_name].append(
                            Assets_dictionary)

                    elif GroupUnder == 'Liabilitis':

                        Group_Under = AccountLedger.objects.get(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).AccountGroupUnder
                        Group_name = AccountGroup.objects.get(
                            AccountGroupID=Group_Under, CompanyID=CompanyID).AccountGroupName

                        ledgerpost_ins = LedgerPosting.objects.filter(
                            LedgerID=LedgerID, Date__gte=FromDate, Date__lte=ToDate, CompanyID=CompanyID)

                        # for consolidated start
                        liabilites_Tot_Credit = 0
                        liabilites_Tot_Debit = 0
                        for lpi in ledgerpost_ins:
                            liabilites_Tot_Debit = + float(lpi.Debit)
                            liabilites_Tot_Credit = + float(lpi.Credit)
                        liablities_balance = float(
                            liabilites_Tot_Credit) - float(liabilites_Tot_Debit)

                        dic_exGrp_liabilities = {"GroupName": str(
                            Group_name), "Balance": float(liablities_balance)}

                        if float(Balance) <= 0:
                            Balance = abs(Balance)
                        else:
                            Balance = float(Balance) * -1

                        print(Balance)

                        if not Group_name in name_exist_liabilities:
                            # name_exist.append(Group_name)
                            dic_exGrp_liabilities = {
                                "Balance": float(Balance)
                            }
                            name_exist_liabilities[Group_name] = dic_exGrp_liabilities
                        else:
                            b = name_exist_liabilities[Group_name]["Balance"]
                            name_exist_liabilities[Group_name]["Balance"] = b + \
                                float(Balance)

                        TotalLiabilitis += Balance
                        Liabilitis_dictionary = {"LedgerID": LedgerID, "LedgerName": LedgerName,
                                                 "Balance": Balance, "GroupUnder": GroupUnder, }

                        # Liabilitis_Array.append(Liabilitis_dictionary)

                        if not Group_name in name_exist_detailed_liabilities:
                            name_exist_detailed_liabilities[Group_name] = []
                        name_exist_detailed_liabilities[Group_name].append(
                            Liabilitis_dictionary)

                final_liabilities_arr.append(name_exist_liabilities)
                final_asset_arr.append(name_exist_asset)

                Liabilitis_Array.append(name_exist_detailed_liabilities)
                Assets_Array.append(name_exist_detailed_asset)

                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                    stock_instances = StockRate.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                    for stock_instance in stock_instances:
                        TotalCoast += stock_instance.Cost

            LiablityPCons = []
            for i in final_liabilities_arr[0]:
                myDic = {
                    'GroupName': i,
                    'Balance': float(final_liabilities_arr[0][i]['Balance'])
                }
                LiablityPCons.append(myDic)

            AssetCons = []
            for i in final_asset_arr[0]:
                myDic = {
                    'GroupName': i,
                    'Balance': float(final_asset_arr[0][i]['Balance'])
                }
                AssetCons.append(myDic)

            # opening balance difference

            total_debit_LoB = 0
            total_credit_LoB = 0
            ledger_instances_LoB = LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherType='LOB', BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            for ledger_instance in ledger_instances_LoB:
                total_debit_LoB += ledger_instance.Debit
                total_credit_LoB += ledger_instance.Credit

            openingBalance_differece = 0
            if (total_debit_LoB > total_credit_LoB):
                openingBalance_differece = total_debit_LoB - total_credit_LoB
            elif(total_credit_LoB > total_debit_LoB):
                openingBalance_differece = total_credit_LoB - total_debit_LoB

            # profit & loss data START
            ManualOpeningStock = 0
            ManualClosingStock = 0
            profit_loss_data = profitAndLoss_excel_data(
                1, CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, FromDate, request, ManualOpeningStock, ManualClosingStock)
            # ===END===
            new_data = balanceSheet_balancing(profit_loss_data, Assets_Array, Liabilitis_Array, TotalAssets,
                                              TotalLiabilitis, TotalCoast, AssetCons, LiablityPCons, openingBalance_differece)

            response_data = {
                "StatusCode": 6000,
                "AssetsData": Assets_Array,
                "LiabilitisData": Liabilitis_Array,
                "TotalAssets": TotalAssets,
                "TotalLiabilitis": TotalLiabilitis,
                "TotalCoast": TotalCoast,
                "AssetCons": AssetCons,
                "LiablityPCons": LiablityPCons,
                "openingBalance_difference": openingBalance_differece,
                "data": new_data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Datas During this Time Periods!"
            }
            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def DayBook(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    BranchID = data['BranchID']
    Date = data['Date']
    PriceRounding = data['PriceRounding']
    summary_count = 0
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date=Date).exists():
        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Date=Date)
        voucher_types = ledger_instances.values_list('VoucherType')
        test_arr = []

        summary_final_all = []
        summary_final_modi = []
        summary_final_Delt = []
        detailed_final = []
        
        for voucherType in voucher_types:
            if voucherType[0] not in test_arr:
                test_arr.append(voucherType[0])

        for ta in test_arr:
            ledger_voucher_group_instances = ledger_instances.filter(
                VoucherType=ta)
            ledger_voucher_instances_modi = ledger_instances.filter(
                VoucherType=ta, Action='M')
            ledger_voucher_instances_Delt = LedgerPosting_Log.objects.filter(
                VoucherType=ta, Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date)
            # count1 = ledger_voucher_group_instances.count()
            list_byID = ledger_voucher_group_instances.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID = []
            [not_dupli_list_byID.append(
                x) for x in list_byID if x not in not_dupli_list_byID]
            count = len(not_dupli_list_byID)

            list_byID_modi = ledger_voucher_instances_modi.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_modi = []
            [not_dupli_list_byID_modi.append(
                x) for x in list_byID_modi if x not in not_dupli_list_byID_modi]
            count_modi = len(not_dupli_list_byID_modi)

            list_byID_delt = ledger_voucher_instances_Delt.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_delt = []
            [not_dupli_list_byID_delt.append(
                x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]
            count_delt = len(not_dupli_list_byID_delt)
           
            vouch_list = []
            if ta == "SI":
                sales_instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=not_dupli_list_byID)
                sales_instances_modif = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=not_dupli_list_byID_modi)
                sales_instances_delt = SalesMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = sales_instances.count()
                summary_count_modif = sales_instances_modif.count()
                summary_count_delt = sales_instances_delt.count()
                sales_grand_total = sales_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = sales_grand_total['GrandTotal__sum']
                sales_grand_total_modif = sales_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = sales_grand_total_modif['GrandTotal__sum']
                sales_grand_total_delt = sales_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PI":
                purchase_instances = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=not_dupli_list_byID)
                purchase_instances_modif = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=not_dupli_list_byID_modi)
                purchase_instances_delt = PurchaseMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = purchase_instances.count()
                summary_count_modif = purchase_instances_modif.count()
                summary_count_delt = purchase_instances_delt.count()
                purchase_grand_total = purchase_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = purchase_grand_total['GrandTotal__sum']
                purchase_grand_total_modif = purchase_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = purchase_grand_total_modif['GrandTotal__sum']
                purchase_grand_total_delt = purchase_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "SR":
                sales_return_instances = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=not_dupli_list_byID)
                sales_return_instances_modif = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=not_dupli_list_byID_modi)
                sales_return_instances_delt = SalesReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = sales_return_instances.count()
                summary_count_modif = sales_return_instances_modif.count()
                summary_count_delt = sales_return_instances_delt.count()
                sales_return_grand_total = sales_return_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = sales_return_grand_total['GrandTotal__sum']
                sales_return_grand_total_modif = sales_return_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = sales_return_grand_total_modif['GrandTotal__sum']
                sales_return_grand_total_delt = sales_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PR":
                purchase_return_instances = PurchaseReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=not_dupli_list_byID)
                purchase_return_instances_modif = PurchaseReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=not_dupli_list_byID_modi)
                purchase_return_instances_delt = PurchaseReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = purchase_return_instances.count()
                summary_count_modif = purchase_return_instances_modif.count()
                summary_count_delt = purchase_return_instances_delt.count()
                purchase_return_grand_total = purchase_return_instances.aggregate(
                    Sum('GrandTotal'))
                grand_total = purchase_return_grand_total['GrandTotal__sum']
                purchase_return_grand_total_modif = purchase_return_instances_modif.aggregate(
                    Sum('GrandTotal'))
                grand_total_modif = purchase_return_grand_total_modif['GrandTotal__sum']
                purchase_return_grand_total_delt = purchase_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "CP" or ta == "BP":
                payment_instances = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, PaymentMasterID__in=not_dupli_list_byID)
                payment_instances_modif = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, PaymentMasterID__in=not_dupli_list_byID_modi)
                payment_instances_delt = PaymentMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = payment_instances.count()
                summary_count_modif = payment_instances_modif.count()
                summary_count_delt = payment_instances_delt.count()
                payment_grand_total = payment_instances.aggregate(
                    Sum('TotalAmount'))
                grand_total = payment_grand_total['TotalAmount__sum']
                payment_grand_total_modif = payment_instances_modif.aggregate(
                    Sum('TotalAmount'))
                grand_total_modif = payment_grand_total_modif['TotalAmount__sum']
                payment_grand_total_delt = payment_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = payment_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)
            elif ta == "CR" or ta == "BR":
                receipt_instances = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, ReceiptMasterID__in=not_dupli_list_byID)
                receipt_instances_modif = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, BranchID=BranchID, ReceiptMasterID__in=not_dupli_list_byID_modi)
                receipt_instances_delt = ReceiptMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count = receipt_instances.count()
                summary_count_modif = receipt_instances_modif.count()
                summary_count_delt = receipt_instances_delt.count()
                receipt_grand_total = receipt_instances.aggregate(
                    Sum('TotalAmount'))
                grand_total = receipt_grand_total['TotalAmount__sum']
                receipt_grand_total_modif = receipt_instances_modif.aggregate(
                    Sum('TotalAmount'))
                grand_total_modif = receipt_grand_total_modif['TotalAmount__sum']
                receipt_grand_total_delt = receipt_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = receipt_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)

            VoucherName = get_VoucherName(ta)
            if summary_count > 0 and ta in vouch_list:
                summary_dic = {
                    'particular': VoucherName,
                    'trans_count': summary_count,
                    'Amount': grand_total
                }
                summary_final_all.append(summary_dic)

            if summary_count_modif > 0 and ta in vouch_list:
                summary_dic_modi = {
                    'particular': VoucherName,
                    'trans_count': summary_count_modif,
                    'Amount': grand_total_modif
                }
                summary_final_modi.append(summary_dic_modi)

            if summary_count_delt > 0 and ta in vouch_list:
                summary_dic_dlt = {
                    'particular': VoucherName,
                    'trans_count': summary_count_delt,
                    'Amount': grand_total_delt
                }
                summary_final_Delt.append(summary_dic_dlt)

            # list_byID_modi = ledger_voucher_instances_modi.values_list(
            #             'VoucherMasterID', flat=True)
            # not_dupli_list_byID_modi = []
            # [not_dupli_list_byID_modi.append(x) for x in list_byID_modi if x not in not_dupli_list_byID_modi]
            # count_modi = len(not_dupli_list_byID_modi)

            # count_modi = ledger_voucher_instances_modi.count()
            # list_byID_delt = ledger_voucher_instances_Delt.values_list(
            #             'VoucherMasterID', flat=True)
            # not_dupli_list_byID_delt = []
            # [not_dupli_list_byID_delt.append(x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]
            # count_delt = len(not_dupli_list_byID_delt)

            # count_delt = ledger_voucher_instances_Delt.count()
            # Amount = 0
            # Amount_modi = 0
            # Amount_delt = 0
            # VoucherName = get_VoucherName(ta)
            # if count > 0:
            #     total_debit_daybk = ledger_voucher_group_instances.aggregate(Sum('Debit'))
            #     total_debit_daybk = total_debit_daybk['Debit__sum']
            #     total_credit = ledger_voucher_group_instances.aggregate(Sum('Credit'))
            #     total_credit = total_credit['Credit__sum']
            #     Amount = float(total_debit_daybk) - float(total_credit)
            #     # for lgp in ledger_voucher_group_instances:
            #     #     Amount += lgp.Debit
            #     summary_dic = {
            #         'particular': VoucherName,
            #         'trans_count': count,
            #         'Amount': total_debit_daybk
            #     }
            #     summary_final_all.append(summary_dic)

            # if count_modi > 0:
            #     total_debit_daybk_modi = ledger_voucher_instances_modi.aggregate(Sum('Debit'))
            #     total_debit_daybk_modi = total_debit_daybk_modi['Debit__sum']
            #     total_credit_modi = ledger_voucher_instances_modi.aggregate(Sum('Credit'))
            #     total_credit_modi = total_credit_modi['Credit__sum']
            #     Amount_modi = float(total_debit_daybk_modi) - float(total_credit_modi)
            #     # for lmd in ledger_voucher_instances_modi:
            #     #     Amount_modi += lmd.Debit
            #     summary_dic_modi = {
            #         'particular': VoucherName,
            #         'trans_count': count_modi,
            #         'Amount': total_debit_daybk_modi
            #     }
            #     summary_final_modi.append(summary_dic_modi)

            # if count_delt > 0:
            #     total_debit_daybk_delt = ledger_voucher_instances_Delt.aggregate(Sum('Debit'))
            #     total_debit_daybk_delt = total_debit_daybk_delt['Debit__sum']
            #     total_credit_modi_delt = ledger_voucher_instances_Delt.aggregate(Sum('Credit'))
            #     total_credit_modi_delt = total_credit_modi_delt['Credit__sum']
            #     Amount_delt = float(total_debit_daybk_delt) - float(total_credit_modi_delt)
            #     # for ldt in ledger_voucher_instances_Delt:
            #     #     Amount_delt += ldt.Debit
            #     summary_dic_dlt = {
            #         'particular': VoucherName,
            #         'trans_count': count_delt,
            #         'Amount': total_debit_daybk_delt
            #     }
            #     summary_final_Delt.append(summary_dic_dlt)

            # summary end here

            ledger_ids = ledger_voucher_group_instances.values_list('LedgerID')
            test_arr_ledger = []
            for ledger_id in ledger_ids:
                if ledger_id[0] not in test_arr_ledger:
                    test_arr_ledger.append(ledger_id[0])

            account_ledger_insts = AccountLedger.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=test_arr_ledger)

            for al in account_ledger_insts:
                LedgerName = al.LedgerName
                ledgers_byId = ledger_instances.filter(
                    LedgerID=al.LedgerID, VoucherType=ta)

                # detail_count = ledgers_byId.count()
                list_byID_detail = ledgers_byId.values_list(
                    'VoucherMasterID', flat=True)
                not_dupli_list_byID_detail = []
                [not_dupli_list_byID_detail.append(
                    x) for x in list_byID_detail if x not in not_dupli_list_byID_detail]
                detail_count = len(not_dupli_list_byID_detail)

                detail_amt = 0
                total_debit_daybk_ = ledgers_byId.aggregate(Sum('Debit'))
                total_debit_daybk_ = total_debit_daybk_['Debit__sum']
                total_credit_modi_ = ledgers_byId.aggregate(Sum('Credit'))
                total_credit_modi_ = total_credit_modi_['Credit__sum']
                detail_amt = float(total_debit_daybk_) - \
                    float(total_credit_modi_)
                # for ldgs in ledgers_byId:
                #     detail_amt += ldgs.Debit
                detaild_dic = {
                    'particular': VoucherName,
                    'LedgerName': LedgerName,
                    'LedgerID': al.LedgerID,
                    'trans_count': detail_count,
                    'Amount': detail_amt
                }
                detailed_final.append(detaild_dic)
             # New Design Function Start
            summary_final = []
            toatl__label_dic = {
                'particular': "Total Active Transactions",
                'trans_count': "",
                'Amount': ""
            }
            modified__label_dic = {
                'particular': "Modified Transactions",
                'trans_count': "",
                'Amount': ""
            }
            deleted__label_dic = {
                'particular': "Deleted Transactions",
                'trans_count': "",
                'Amount': ""
            }
            if summary_final_all:
                summary_final.append(toatl__label_dic)
                for i in summary_final_all:
                    summary_final.append(i)
            if summary_final_modi:
                summary_final.append(modified__label_dic)
                for i in summary_final_modi:
                    summary_final.append(i)
            if summary_final_Delt:
                summary_final.append(deleted__label_dic)
                for i in summary_final_Delt:
                    summary_final.append(i)

            # New Design Function End
        response_data = {
            "StatusCode": 6000,
            "summary_final_all": summary_final_all,
            "summary_final_modi": summary_final_modi,
            "summary_final_Delt": summary_final_Delt,
            "detailed_final": detailed_final,
            "summary_final": summary_final,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    elif LedgerPosting_Log.objects.filter(Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date).exists():
        ledgerLog_instances = LedgerPosting_Log.objects.filter(
            Action='D', CompanyID=CompanyID, BranchID=BranchID, Date=Date)
        voucher_types = ledgerLog_instances.values_list('VoucherType')
        test_arr = []
        summary_final_Delt = []
        for voucherType in voucher_types:
            if voucherType[0] not in test_arr:
                test_arr.append(voucherType[0])

        for ta in test_arr:
            ledger_voucher_instances_Delt = ledgerLog_instances.filter(
                VoucherType=ta)
            # count_delt = ledger_voucher_instances_Delt.count()
            list_byID_delt = ledger_voucher_instances_Delt.values_list(
                'VoucherMasterID', flat=True)
            not_dupli_list_byID_delt = []
            [not_dupli_list_byID_delt.append(
                x) for x in list_byID_delt if x not in not_dupli_list_byID_delt]

            vouch_list = []
            if ta == "SI":
                sales_instances_delt = SalesMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = sales_instances_delt.count()
                sales_grand_total_delt = sales_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PI":
                purchase_instances_delt = PurchaseMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = purchase_instances_delt.count()
                purchase_grand_total_delt = purchase_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "SR":
                sales_return_instances_delt = SalesReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = sales_return_instances_delt.count()
                sales_return_grand_total_delt = sales_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = sales_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "PR":
                purchase_return_instances_delt = PurchaseReturnMaster_Log.objects.filter(
                    CompanyID=CompanyID, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = purchase_return_instances_delt.count()
                purchase_return_grand_total_delt = purchase_return_instances_delt.aggregate(
                    Sum('GrandTotal'))
                grand_total_delt = purchase_return_grand_total_delt['GrandTotal__sum']
                vouch_list.append(ta)
            elif ta == "CP" or ta == "BP":
                payment_instances_delt = PaymentMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = payment_instances_delt.count()
                payment_grand_total_delt = payment_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = payment_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)
            elif ta == "CR" or ta == "BR":
                receipt_instances_delt = ReceiptMaster_Log.objects.filter(
                    CompanyID=CompanyID, VoucherType=ta, Action="D", BranchID=BranchID, TransactionID__in=not_dupli_list_byID_delt)
                summary_count_delt = receipt_instances_delt.count()
                receipt_grand_total_delt = receipt_instances_delt.aggregate(
                    Sum('TotalAmount'))
                grand_total_delt = receipt_grand_total_delt['TotalAmount__sum']
                vouch_list.append(ta)

            VoucherName = get_VoucherName(ta)

            if summary_count_delt > 0 and ta in vouch_list:
                summary_dic_dlt = {
                    'particular': VoucherName,
                    'trans_count': summary_count_delt,
                    'Amount': grand_total_delt
                }
                summary_final_Delt.append(summary_dic_dlt)

            # count_delt = len(not_dupli_list_byID_delt)
            # Amount_delt = 0
            # VoucherName = get_VoucherName(ta)

            # if count_delt > 0:
            #     total_debit_daybk_delt = ledger_voucher_instances_Delt.aggregate(Sum('Debit'))
            #     total_credit_modi_delt = ledger_voucher_instances_Delt.aggregate(Sum('Credit'))
            #     Amount_delt = float(total_debit_daybk_delt) - float(total_credit_modi_delt)
            #     # for ldt in ledger_voucher_instances_Delt:
            #     #     Amount_delt += ldt.Debit
            #     summary_dic_dlt = {
            #         'particular': VoucherName,
            #         'trans_count': count_delt,
            #         'Amount': Amount_delt
            #     }
            #     summary_final_Delt.append(summary_dic_dlt)
        response_data = {
            "StatusCode": 6000,
            "summary_final_all": [],
            "summary_final_modi": [],
            "summary_final_Delt": summary_final_Delt,
            "detailed_final": []
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas on this day!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def cash_book(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    BranchID = data['BranchID']
    FromDate = data['FromDate']
    ToDate = data['ToDate']
    PriceRounding = data['PriceRounding']
    CashLedgers = data['CashLedgers']
    ManualOpeningBalance = data['ManualOpeningBalance']
    is_manualOpening = data['is_manualOpening']

    if not CashLedgers:
        CashLedgers = []
        # cash_ledger_ins = AccountLedger.objects.filter(
        #     CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=9)
        # for i in cash_ledger_ins:
        #     CashLedgers.append(i.LedgerID)

    Balance = ManualOpeningBalance
    OpeningBalance = 0
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers, Date__gte=FromDate, Date__lte=ToDate).exists():

        if float(ManualOpeningBalance) == 0:
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers).order_by('Date')
        else:
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers, Date__gte=FromDate, Date__lte=ToDate).order_by('Date')

        serialized = LedgerReportLedgerWiseSerializer(ledger_instances, many=True, context={
                                                      "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        orderdDict = serialized.data
        jsnDatas = convertOrderdDict(orderdDict)

        virtual_array = []
        last_data = []
        new_last_data = []
        ob_array = []

        for i in jsnDatas:
            Debit = i['Debit']
            Credit = i['Credit']
            LedgerID = i['LedgerID']
            LedgerName = i['LedgerName']
            VoucherType = i['VoucherType']
            VoucherNo = i['VoucherNo']
            Date = i['Date']
            Unq_id = i['Unq_id']
            Balance = (float(Balance) + float(Debit)) - \
                float(Credit)

            i['Balance'] = round(Balance, PriceRounding)
            Debit = float(Debit)
            Credit = float(Credit)

            virtual_dictionary = {"Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding), "LedgerID": LedgerID, "LedgerName": LedgerName,
                                  "VoucherType": VoucherType, "VoucherNo": VoucherNo, "Date": Date, "Balance": round(Balance, PriceRounding), "Unq_id": Unq_id}

            virtual_array.append(virtual_dictionary)

        for i in virtual_array:
            date = i["Date"]

            if FromDate > date:
                ob_array.append(i)
            if FromDate <= date and ToDate >= date:
                last_data.append(i)
                new_last_data.append(i)

        if ob_array:
            last_dict = ob_array[-1]
            OpeningBalance = last_dict['Balance']
        if last_data:
            TotalDebit = 0
            TotalCredit = 0
            TotalBalance = 0
            for data in last_data:
                TotalDebit += data['Debit']
                TotalCredit += data['Credit']
                # TotalBalance += data['Balance']

            if is_manualOpening == True:
                OpeningBalance = float(ManualOpeningBalance)

            if OpeningBalance > 0:
                TotalDebit = float(TotalDebit) + float(OpeningBalance)
            elif OpeningBalance < 0:
                TotalCredit = float(TotalCredit) + float(OpeningBalance)
            TotalBalance = float(TotalDebit) - float(TotalCredit)

            # New Style Function Start
            opening_cashbook = {"Debit": OpeningBalance, "Credit": "", "LedgerID": "", "LedgerName": "Opening Balance",
                                "VoucherType": "", "VoucherNo": "", "Date": "", "Balance": OpeningBalance, "Unq_id": ""}
            new_last_data.insert(0, opening_cashbook)
            total_cashbook = {"Debit": TotalDebit, "Credit": TotalCredit, "LedgerID": "", "LedgerName": "Toatl",
                              "VoucherType": "", "VoucherNo": "", "Date": "", "Balance": TotalBalance, "Unq_id": ""}
            new_last_data.append(total_cashbook)
            # New Style Function End

        response_data = {
            "StatusCode": 6000,
            "data": last_data,
            "new_data": new_last_data,
            "OpeningBalance": OpeningBalance,
            "TotalDebit": round(TotalDebit, PriceRounding),
            "TotalCredit": round(TotalCredit, PriceRounding),
            "TotalBalance": round(TotalBalance, PriceRounding),
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During This Time!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def bank_book(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    BranchID = data['BranchID']
    FromDate = data['FromDate']
    ToDate = data['ToDate']
    PriceRounding = data['PriceRounding']
    CashLedgers = data['CashLedgers']
    ManualOpeningBalance = data['ManualOpeningBalance']
    is_manualOpening = data['is_manualOpening']

    if not CashLedgers:
        CashLedgers = []
        cash_ledger_ins = AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=8)
        for i in cash_ledger_ins:
            CashLedgers.append(i.LedgerID)

    Balance = ManualOpeningBalance
    OpeningBalance = 0
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers, Date__gte=FromDate, Date__lte=ToDate).exists():

        if float(ManualOpeningBalance) == 0:
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers).order_by('Date')
        else:
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=CashLedgers, Date__gte=FromDate, Date__lte=ToDate).order_by('Date')

        serialized = LedgerReportLedgerWiseSerializer(ledger_instances, many=True, context={
                                                      "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        orderdDict = serialized.data
        jsnDatas = convertOrderdDict(orderdDict)

        virtual_array = []
        last_data = []
        new_last_data = []
        ob_array = []

        for i in jsnDatas:
            Debit = i['Debit']
            Credit = i['Credit']
            LedgerID = i['LedgerID']
            LedgerName = i['LedgerName']
            VoucherType = i['VoucherType']
            VoucherNo = i['VoucherNo']
            Date = i['Date']
            Balance = (float(Balance) + float(Debit)) - \
                float(Credit)

            i['Balance'] = round(Balance, PriceRounding)
            Debit = float(Debit)
            Credit = float(Credit)

            virtual_dictionary = {"Debit": round(Debit, PriceRounding), "Credit": round(Credit, PriceRounding), "LedgerID": LedgerID, "LedgerName": LedgerName,
                                  "VoucherType": VoucherType, "VoucherNo": VoucherNo, "Date": Date, "Balance": round(Balance, PriceRounding)}

            virtual_array.append(virtual_dictionary)

        for i in virtual_array:
            date = i["Date"]

            if FromDate > date:
                ob_array.append(i)
            if FromDate <= date and ToDate >= date:
                last_data.append(i)
                new_last_data.append(i)

        if ob_array:
            last_dict = ob_array[-1]
            OpeningBalance = last_dict['Balance']
        if last_data:
            TotalDebit = 0
            TotalCredit = 0
            TotalBalance = 0
            for data in last_data:
                TotalDebit += data['Debit']
                TotalCredit += data['Credit']
                # TotalBalance += data['Balance']

            if is_manualOpening == True:
                OpeningBalance = float(ManualOpeningBalance)

            if OpeningBalance > 0:
                TotalDebit = float(TotalDebit) + float(OpeningBalance)
            elif OpeningBalance < 0:
                TotalCredit = float(TotalCredit) + float(OpeningBalance)
            TotalBalance = float(TotalDebit) - float(TotalCredit)

            # New Style Function Start
            opening_cashbook = {"Debit": OpeningBalance, "Credit": "", "LedgerID": "", "LedgerName": "Opening Balance",
                                "VoucherType": "", "VoucherNo": "", "Date": "", "Balance": OpeningBalance, "Unq_id": ""}
            new_last_data.insert(0, opening_cashbook)
            total_cashbook = {"Debit": TotalDebit, "Credit": TotalCredit, "LedgerID": "", "LedgerName": "Toatl",
                              "VoucherType": "", "VoucherNo": "", "Date": "", "Balance": TotalBalance, "Unq_id": ""}
            new_last_data.append(total_cashbook)
            # New Style Function End

        response_data = {
            "StatusCode": 6000,
            "data": last_data,
            "new_data": new_last_data,
            "OpeningBalance": OpeningBalance,
            "TotalDebit": round(TotalDebit, PriceRounding),
            "TotalCredit": round(TotalCredit, PriceRounding),
            "TotalBalance": round(TotalBalance, PriceRounding),
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During This Time!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def outstanding_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    Type = data['Type']
    BranchID = data['BranchID']
    ToDate = data['ToDate']
    PriceRounding = data['PriceRounding']
    RouteLedgers = data['RouteLedgers']
    ledger_id_list = []
    if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, RouteID__in=RouteLedgers).exists():
        party_ins = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, RouteID__in=RouteLedgers)
        for i in party_ins:
            ledger_id_list.append(i.LedgerID)
    else:
        party_ins = Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        for i in party_ins:
            ledger_id_list.append(i.LedgerID)

    test_arr = []
    final_arr = []
    new_final_arr = []
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_id_list, Date__lte=ToDate).exists():
        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_id_list, Date__lte=ToDate)

        ledger_ids = ledger_instances.values_list('LedgerID')
        for ledger_id in ledger_ids:
            if ledger_id[0] not in test_arr:
                test_arr.append(ledger_id[0])

        account_ledgers = AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=test_arr)
        serialized = LedgerReportSerializer(account_ledgers, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        jsnDatas = convertOrderdDict(serialized.data)
        print(Type)
        tot_Debit = 0
        tot_Credit = 0
        for i in jsnDatas:
            if Type == None:
                final_arr.append(i)
                tot_Debit += i['Debit']
                tot_Credit += i['Credit']
            elif Type == "creditors":
                if i['Debit'] == 0 and i['Credit'] > 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
            elif Type == "debitors":
                if i['Debit'] > 0 and i['Credit'] == 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
            elif Type == "zero_balance":
                if i['Debit'] == 0 and i['Credit'] == 0:
                    final_arr.append(i)
                    new_final_arr.append(i)

                    tot_Debit += i['Debit']
                    tot_Credit += i['Credit']
        total_dic = {
            "LedgerName": "Total",
            "Debit": tot_Debit,
            "Credit": tot_Credit,
        }
        final_arr.append(total_dic)

        response_data = {
            "StatusCode": 6000,
            "data": final_arr,
            "new_data": new_final_arr,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "No Datas During This Time!"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def ledgerReport_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)
    try:
        CreatedUserID = int(request.GET.get('CreatedUserID'))
    except:
        CreatedUserID = ""

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    try:
        ID = int(request.GET.get('ID'))
    except:
        ID = ""

    try:
        ManualOpeningBalance = int(request.GET.get('ManualOpeningBalance'))
    except:
        ManualOpeningBalance = ""

    try:
        value = int(request.GET.get('value'))
    except:
        value = 0

    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')

    print(CompanyID, CreatedUserID, PriceRounding, BranchID, FromDate,
          ToDate, ID, value, ManualOpeningBalance, '****************')
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Ledger Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = ledgerReport_excel_data(CompanyID, CreatedUserID, PriceRounding,
                                   BranchID, FromDate, ToDate, ID, value, ManualOpeningBalance)

    # ===============  adding Ledger Report sheet ============
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                               'font: colour white, bold True;')

    export_to_excel_ledgerReport(wb, data, ID, FromDate)

    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def trialBalance_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)
    try:
        CreatedUserID = int(request.GET.get('CreatedUserID'))
    except:
        CreatedUserID = ""

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    ToDate = request.GET.get('ToDate')

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="TrialBalance Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = trialBalance_excel_data(
        CompanyID.pk, CreatedUserID, PriceRounding, BranchID, ToDate, request)

    # ===============  adding Ledger Report sheet ============
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                               'font: colour white, bold True;')

    export_to_excel_trialBalance(wb, data)

    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def profitAndLoss_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)
    try:
        CreatedUserID = int(request.GET.get('CreatedUserID'))
    except:
        CreatedUserID = ""

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    try:
        ManualOpeningStock = int(request.GET.get('ManualOpeningStock'))
    except:
        ManualClosingStock = ""

    try:
        ManualClosingStock = int(request.GET.get('ManualClosingStock'))
    except:
        ManualClosingStock = ""

    ToDate = request.GET.get('ToDate')
    FromDate = request.GET.get('FromDate')
    key = int(request.GET.get('key'))

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Profit and Loss Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = profitAndLoss_excel_data(key, CompanyID, CreatedUserID, PriceRounding,
                                    BranchID, ToDate, FromDate, request, ManualOpeningStock, ManualClosingStock)

    export_to_excel_profitAndLoss(wb, data, key)

    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def balanceSheet_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)
    try:
        CreatedUserID = int(request.GET.get('CreatedUserID'))
    except:
        CreatedUserID = ""

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    ToDate = request.GET.get('ToDate')
    FromDate = request.GET.get('FromDate')

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="BalanceSheet Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = balanceSheet_excel_data(
        CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, FromDate, request)
    ManualOpeningStock = 0
    ManualClosingStock = 0
    profit_loss_data = profitAndLoss_excel_data(1,
                                                CompanyID, CreatedUserID, PriceRounding, BranchID, ToDate, FromDate, request, ManualOpeningStock, ManualClosingStock)
    # ===============  adding Ledger Report sheet ============
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                               'font: colour white, bold True;')
    export_to_excel_balanceSheet(wb, data, profit_loss_data)

    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def DayBook_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    Date = request.GET.get('Date')
    Type = request.GET.get('Type')

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="DayBook Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    data = DayBook_excel_data(CompanyID, BranchID, Date, PriceRounding, Type)
    print(data)
    title = str(CompanyID.CompanyName) + str(",")+str(Date)
    export_to_excel_DayBook(wb, data, Type, title)

    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def outStandingReport_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    ToDate = request.GET.get('ToDate')
    CreatedUserID = request.GET.get('CreatedUserID')
    Type = request.GET.get('VoucherType')
    LedgerList = request.GET.getlist('CashLedgers')
    print(Type, type(LedgerList), LedgerList)
    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        print(str(x).split(','))
        test_list = str(x).split(',')
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list

    RouteLedgers = LedgerList

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Receipt Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    data = outStandingReport_excel_data(
        CompanyID, BranchID, PriceRounding, RouteLedgers, ToDate, Type)

    print(data)
    title = str(CompanyID.CompanyName) + str(",") + str(ToDate)
    export_to_excel_outStandingReport(wb, data, title, Type)

    wb.save(response)
    return response
