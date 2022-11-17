from brands.models import AccountLedger, Activity_Log, UserAdrress, VoucherNoTable, SalesEstimateMaster, SalesEstimateMaster_Log, SalesEstimateDetails, SalesEstimateDetails_Log, GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.salesEstimates.serializers import SalesEstimateMasterSerializer, SalesEstimateMasterRestSerializer, SalesEstimateDetailsSerializer, SalesEstimateDetailsRestSerializer, SalesEstimateMaster1RestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.salesEstimates.functions import generate_serializer_errors
from rest_framework import status
from api.v10.salesEstimates.functions import get_auto_id, get_auto_idMaster
import datetime
from main.functions import converted_float, get_LedgerBalance, get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v10.sales.functions import get_Genrate_VoucherNo
from django.db import transaction, IntegrityError
import re
import sys
import os
from main.functions import update_voucher_table
from django.db.models import Q, Prefetch, Sum


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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_salesEstimate(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            Date = data['Date']
            DeliveryDate = data['DeliveryDate']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            BillDiscAmt = data['BillDiscAmt']
            BillDiscPercent = data['BillDiscPercent']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            IsActive = data['IsActive']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalDiscount = data['TotalDiscount']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']
            
            try:
                EmployeeID = data["EmployeeID"]
            except:
                EmployeeID = None

            Action = "A"

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""
            
            try:
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""

            VoucherType = "SE"

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "SE"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1
                
            try:
                ReffNo = data['ReffNo']
            except:
                ReffNo = ""

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
                
            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = UserAdrress.objects.get(
                        id=BillingAddress)

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SalesEstimateOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesEstimateMaster_Log, BranchID, CompanyID, "SE")
                is_SalesEstimateOK = True
            elif is_voucherExist == False:
                is_SalesEstimateOK = True
            else:
                is_SalesEstimateOK = False

            if is_SalesEstimateOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)
                SalesEstimateMasterID = get_auto_idMaster(
                    SalesEstimateMaster, BranchID, CompanyID)

                LogID = SalesEstimateMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=SalesEstimateMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    DeliveryDate=DeliveryDate,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    BillDiscAmt=BillDiscAmt,
                    BillDiscPercent=BillDiscPercent,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalDiscount=TotalDiscount,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    ReffNo=ReffNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
                    EmployeeID=EmployeeID,
                )

                sales_estimate_instance = SalesEstimateMaster.objects.create(
                    CompanyID=CompanyID,
                    SalesEstimateMasterID=SalesEstimateMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    DeliveryDate=DeliveryDate,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    BillDiscAmt=BillDiscAmt,
                    BillDiscPercent=BillDiscPercent,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalDiscount=TotalDiscount,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    ReffNo=ReffNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
                    EmployeeID=EmployeeID,
                )

                saleEstimatesDetails = data["saleEstimatesDetails"]
                for saleEstimatesDetail in saleEstimatesDetails:
                    ProductID = saleEstimatesDetail['ProductID']
                    if ProductID:
                        Qty = saleEstimatesDetail['Qty']
                        FreeQty = saleEstimatesDetail['FreeQty']
                        UnitPrice = saleEstimatesDetail['UnitPrice']
                        RateWithTax = saleEstimatesDetail['RateWithTax']
                        PriceListID = saleEstimatesDetail['PriceListID']
                        DiscountPerc = saleEstimatesDetail['DiscountPerc']
                        DiscountAmount = saleEstimatesDetail['DiscountAmount']
                        GrossAmount = saleEstimatesDetail['GrossAmount']
                        TaxableAmount = saleEstimatesDetail['TaxableAmount']
                        VATPerc = saleEstimatesDetail['VATPerc']
                        VATAmount = saleEstimatesDetail['VATAmount']
                        SGSTPerc = saleEstimatesDetail['SGSTPerc']
                        SGSTAmount = saleEstimatesDetail['SGSTAmount']
                        CGSTPerc = saleEstimatesDetail['CGSTPerc']
                        CGSTAmount = saleEstimatesDetail['CGSTAmount']
                        IGSTPerc = saleEstimatesDetail['IGSTPerc']
                        IGSTAmount = saleEstimatesDetail['IGSTAmount']
                        TAX1Perc = saleEstimatesDetail['TAX1Perc']
                        TAX1Amount = saleEstimatesDetail['TAX1Amount']
                        TAX2Perc = saleEstimatesDetail['TAX2Perc']
                        TAX2Amount = saleEstimatesDetail['TAX2Amount']
                        TAX3Perc = saleEstimatesDetail['TAX3Perc']
                        TAX3Amount = saleEstimatesDetail['TAX3Amount']
                        KFCAmount = saleEstimatesDetail['KFCAmount']
                        NetAmount = saleEstimatesDetail['NetAmount']
                        InclusivePrice = saleEstimatesDetail['InclusivePrice']
                        try:
                            BatchCode = saleEstimatesDetail['BatchCode']
                        except:
                            BatchCode = 0
                        try:
                            Description = saleEstimatesDetail["Description"]
                        except:
                            Description = ""

                        try:
                            ProductTaxID = saleEstimatesDetail['ProductTaxID']
                        except:
                            ProductTaxID = ""
                            
                        if not Qty:
                            Qty = 0
                        if not FreeQty:
                            FreeQty = 0

                        SalesEstimateDetailsID = get_auto_id(
                            SalesEstimateDetails, BranchID, CompanyID)

                        SalesEstimateDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesEstimateDetailsID=SalesEstimateDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesEstimateMasterID=SalesEstimateMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description,
                        )

                        SalesEstimateDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            SalesEstimateMaster_LogID=LogID.pk,
                            TransactionID=SalesEstimateDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesEstimateMasterID=SalesEstimateMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description,
                        )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Estimates',
                #              'Create', 'Sale Estimates created successfully.', 'Sale Estimates saved successfully.')
                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "StatusCode": 6000,
                    "id": sales_estimate_instance.id,
                    "message": "Sale Estimates created Successfully!!!",
                    "CashBalance": cash_Balance,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sale Estimates',
                             'Create', 'Sale Estimates created Failed.', 'VoucherNo already exist!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        print("=============================>>>>")
        print(str(e))
        print(err_descrb)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }
        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales Estimate',
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
 
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_salesEstimate(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            salesEstimateMaster_instance = None
            salesEstimateDetails = None

            salesEstimateMaster_instance = SalesEstimateMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            SalesEstimateMasterID = salesEstimateMaster_instance.SalesEstimateMasterID
            BranchID = salesEstimateMaster_instance.BranchID
            VoucherNo = salesEstimateMaster_instance.VoucherNo

            Date = data['Date']
            DeliveryDate = data['DeliveryDate']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            BillDiscAmt = data['BillDiscAmt']
            BillDiscPercent = data['BillDiscPercent']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            IsActive = data['IsActive']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalDiscount = data['TotalDiscount']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']
            
            try:
                EmployeeID = data["EmployeeID"]
            except:
                EmployeeID = None

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""
                
            try:
                ReffNo = data['ReffNo']
            except:
                ReffNo = ""

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
                
            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = UserAdrress.objects.get(
                        id=BillingAddress)

            Action = "M"

            salesEstimateMaster_instance.Date = Date
            salesEstimateMaster_instance.DeliveryDate = DeliveryDate
            salesEstimateMaster_instance.LedgerID = LedgerID
            salesEstimateMaster_instance.PriceCategoryID = PriceCategoryID
            salesEstimateMaster_instance.CustomerName = CustomerName
            salesEstimateMaster_instance.Address1 = Address1
            salesEstimateMaster_instance.Address2 = Address2
            salesEstimateMaster_instance.Notes = Notes
            salesEstimateMaster_instance.FinacialYearID = FinacialYearID
            salesEstimateMaster_instance.TotalTax = TotalTax
            salesEstimateMaster_instance.NetTotal = NetTotal
            salesEstimateMaster_instance.BillDiscAmt = BillDiscAmt
            salesEstimateMaster_instance.BillDiscPercent = BillDiscPercent
            salesEstimateMaster_instance.GrandTotal = GrandTotal
            salesEstimateMaster_instance.RoundOff = RoundOff
            salesEstimateMaster_instance.IsActive = IsActive
            salesEstimateMaster_instance.Action = Action
            salesEstimateMaster_instance.UpdatedDate = today
            salesEstimateMaster_instance.CreatedUserID = CreatedUserID
            salesEstimateMaster_instance.TaxID = TaxID
            salesEstimateMaster_instance.TaxType = TaxType
            salesEstimateMaster_instance.CompanyID = CompanyID
            salesEstimateMaster_instance.TotalGrossAmt = TotalGrossAmt
            salesEstimateMaster_instance.TotalDiscount = TotalDiscount
            salesEstimateMaster_instance.VATAmount = VATAmount
            salesEstimateMaster_instance.SGSTAmount = SGSTAmount
            salesEstimateMaster_instance.CGSTAmount = CGSTAmount
            salesEstimateMaster_instance.IGSTAmount = IGSTAmount
            salesEstimateMaster_instance.TAX1Amount = TAX1Amount
            salesEstimateMaster_instance.TAX2Amount = TAX2Amount
            salesEstimateMaster_instance.TAX3Amount = TAX3Amount
            salesEstimateMaster_instance.Country_of_Supply = Country_of_Supply
            salesEstimateMaster_instance.State_of_Supply = State_of_Supply
            salesEstimateMaster_instance.GST_Treatment = GST_Treatment
            salesEstimateMaster_instance.VAT_Treatment = VAT_Treatment
            salesEstimateMaster_instance.ReffNo = ReffNo
            salesEstimateMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesEstimateMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            salesEstimateMaster_instance.BillingAddress = BillingAddress
            salesEstimateMaster_instance.EmployeeID = EmployeeID
            salesEstimateMaster_instance.save()

            LogID = SalesEstimateMaster_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=SalesEstimateMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                DeliveryDate=DeliveryDate,
                Date=Date,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalTax=TotalTax,
                NetTotal=NetTotal,
                BillDiscAmt=BillDiscAmt,
                BillDiscPercent=BillDiscPercent,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                IsActive=IsActive,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxID=TaxID,
                TaxType=TaxType,
                TotalGrossAmt=TotalGrossAmt,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                VAT_Treatment=VAT_Treatment,
                ReffNo=ReffNo,
                BillingAddress=BillingAddress,
                EmployeeID=EmployeeID
            )

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if SalesEstimateDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                            deleted_detail = SalesEstimateDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk)
                            deleted_detail.delete()

            salesEstimateDetails = data["saleEstimatesDetails"]
            for salesEstimateDetail in salesEstimateDetails:

                unq_id = salesEstimateDetail['unq_id']
                ProductID = salesEstimateDetail['ProductID']
                if ProductID:
                    Qty = salesEstimateDetail['Qty']
                    FreeQty = salesEstimateDetail['FreeQty']
                    UnitPrice = salesEstimateDetail['UnitPrice']
                    RateWithTax = salesEstimateDetail['RateWithTax']
                    PriceListID = salesEstimateDetail['PriceListID']
                    DiscountPerc = salesEstimateDetail['DiscountPerc']
                    DiscountAmount = salesEstimateDetail['DiscountAmount']
                    GrossAmount = salesEstimateDetail['GrossAmount']
                    TaxableAmount = salesEstimateDetail['TaxableAmount']
                    VATPerc = salesEstimateDetail['VATPerc']
                    VATAmount = salesEstimateDetail['VATAmount']
                    SGSTPerc = salesEstimateDetail['SGSTPerc']
                    SGSTAmount = salesEstimateDetail['SGSTAmount']
                    CGSTPerc = salesEstimateDetail['CGSTPerc']
                    CGSTAmount = salesEstimateDetail['CGSTAmount']
                    IGSTPerc = salesEstimateDetail['IGSTPerc']
                    IGSTAmount = salesEstimateDetail['IGSTAmount']
                    TAX1Perc = salesEstimateDetail['TAX1Perc']
                    TAX1Amount = salesEstimateDetail['TAX1Amount']
                    TAX2Perc = salesEstimateDetail['TAX2Perc']
                    TAX2Amount = salesEstimateDetail['TAX2Amount']
                    TAX3Perc = salesEstimateDetail['TAX3Perc']
                    TAX3Amount = salesEstimateDetail['TAX3Amount']
                    KFCAmount = salesEstimateDetail['KFCAmount']
                    NetAmount = salesEstimateDetail['NetAmount']
                    try:
                        BatchCode = salesEstimateDetail['BatchCode']
                    except:
                        BatchCode = 0
                    InclusivePrice = salesEstimateDetail['InclusivePrice']
                    detailID = salesEstimateDetail['detailID']

                    try:
                        ProductTaxID = salesEstimateDetail['ProductTaxID']
                    except:
                        ProductTaxID = ""
                        
                    try:
                        Description = salesEstimateDetail["Description"]
                    except:
                        Description = ""
                        
                    if not Qty:
                        Qty = 0
                    if not FreeQty:
                        FreeQty = 0

                    SalesEstimateDetailsID = get_auto_id(
                        SalesEstimateDetails, BranchID, CompanyID)

                    if detailID == 0:
                        Action = "M"
                        salesDetail_instance = SalesEstimateDetails.objects.get(
                            CompanyID=CompanyID, pk=unq_id)
                        salesDetail_instance.ProductID = ProductID
                        salesDetail_instance.Qty = Qty
                        salesDetail_instance.FreeQty = FreeQty
                        salesDetail_instance.UnitPrice = UnitPrice
                        salesDetail_instance.InclusivePrice = InclusivePrice
                        salesDetail_instance.RateWithTax = RateWithTax
                        salesDetail_instance.PriceListID = PriceListID
                        salesDetail_instance.DiscountPerc = DiscountPerc
                        salesDetail_instance.DiscountAmount = DiscountAmount
                        # salesDetail_instance.AddlDiscPerc = AddlDiscPerc
                        # salesDetail_instance.AddlDiscAmt = AddlDiscAmt
                        salesDetail_instance.GrossAmount = GrossAmount
                        salesDetail_instance.TaxableAmount = TaxableAmount
                        salesDetail_instance.VATPerc = VATPerc
                        salesDetail_instance.VATAmount = VATAmount
                        salesDetail_instance.SGSTPerc = SGSTPerc
                        salesDetail_instance.SGSTAmount = SGSTAmount
                        salesDetail_instance.CGSTPerc = CGSTPerc
                        salesDetail_instance.CGSTAmount = CGSTAmount
                        salesDetail_instance.IGSTPerc = IGSTPerc
                        salesDetail_instance.IGSTAmount = IGSTAmount
                        salesDetail_instance.NetAmount = NetAmount
                        salesDetail_instance.CreatedUserID = CreatedUserID
                        salesDetail_instance.UpdatedDate = today
                        salesDetail_instance.Action = Action
                        salesDetail_instance.CreatedDate = today
                        salesDetail_instance.TAX1Perc = TAX1Perc
                        salesDetail_instance.TAX1Amount = TAX1Amount
                        salesDetail_instance.TAX2Perc = TAX2Perc
                        salesDetail_instance.TAX2Amount = TAX2Amount
                        salesDetail_instance.TAX3Perc = TAX3Perc
                        salesDetail_instance.TAX3Amount = TAX3Amount
                        salesDetail_instance.KFCAmount = KFCAmount
                        salesDetail_instance.BatchCode = BatchCode
                        salesDetail_instance.CompanyID = CompanyID
                        salesDetail_instance.ProductTaxID = ProductTaxID
                        salesDetail_instance.Description = Description

                        salesDetail_instance.save()

                        SalesEstimateDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            SalesEstimateMaster_LogID=LogID.pk,
                            TransactionID=SalesEstimateDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesEstimateMasterID=SalesEstimateMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            # TaxID=TaxID,
                            # TaxType=TaxType,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            ProductTaxID=ProductTaxID,
                            Description=Description,
                        )

                    if detailID == 1:

                        Action = "A"

                        SalesEstimateDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            SalesEstimateMaster_LogID=LogID.pk,
                            TransactionID=SalesEstimateDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesEstimateMasterID=SalesEstimateMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description,
                        )

                        SalesEstimateDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesEstimateDetailsID=SalesEstimateDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesEstimateMasterID=SalesEstimateMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            NetAmount=NetAmount,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description,
                        )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Estimates',
            #              'Edit', 'Sale Estimates Updated successfully.', 'Sale Estimates Updated successfully.')
            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "SalesEstimate Updated Successfully!!!",
                "CashBalance": cash_Balance,
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales Estimate',
                                   'Edit', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_salesEstimateMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    # filterID = data['filterID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        print("filterID==================")
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            is_data_exist = False
            # if filterID == "Pending":
            #     if instances.filter(IsInvoiced="N").exists():
            #         is_data_exist = True
            #         instances = instances.filter(IsInvoiced="N")
            # elif filterID == "Invoiced":
            #     if instances.filter(IsInvoiced="I").exists():
            #         is_data_exist = True
            #         instances = instances.filter(IsInvoiced="I")
            # elif filterID == "Cancelled":
            #     if instances.filter(IsInvoiced="C").exists():
            #         is_data_exist = True
            #         instances = instances.filter(IsInvoiced="C")
            # else:
            is_data_exist = True
            instances = instances

            serialized = SalesEstimateMasterRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

            if is_data_exist == True:
                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Estimates',
                #              'List', 'Sale Estimates List viewed successfully.', 'Sale Estimates List viewed successfully')

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Sales Estimate Not Found!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Estimate Not Found!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesEstimateMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if SalesEstimateMaster.objects.filter(pk=pk).exists():
        instance = SalesEstimateMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SalesEstimateMasterRestSerializer(
            instance, context={"CompanyID": CompanyID})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Estimates', 'View',
        #              'Sale Estimates Single viewed successfully.', 'Sale Estimates Single viewed successfully')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Estimate Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_salesEstimateMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instance = None
    if selecte_ids:
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = SalesEstimateMaster.objects.filter(pk__in=selecte_ids)
    else:
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = SalesEstimateMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            SalesEstimateMasterID = instance.SalesEstimateMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            Date = instance.Date
            LedgerID = instance.LedgerID
            PriceCategoryID = instance.PriceCategoryID
            CustomerName = instance.CustomerName
            Address1 = instance.Address1
            Address2 = instance.Address2
            Notes = instance.Notes
            FinacialYearID = instance.FinacialYearID
            TotalTax = instance.TotalTax
            NetTotal = instance.NetTotal
            BillDiscAmt = instance.BillDiscAmt
            GrandTotal = instance.GrandTotal
            RoundOff = instance.RoundOff
            IsActive = instance.IsActive
            DeliveryDate = instance.DeliveryDate
            TotalGrossAmt = instance.TotalGrossAmt
            TotalDiscount = instance.TotalDiscount
            VATAmount = instance.VATAmount
            SGSTAmount = instance.SGSTAmount
            CGSTAmount = instance.CGSTAmount
            IGSTAmount = instance.IGSTAmount
            TAX1Amount = instance.TAX1Amount
            TAX2Amount = instance.TAX2Amount
            TAX3Amount = instance.TAX3Amount
            Country_of_Supply = instance.Country_of_Supply
            State_of_Supply = instance.State_of_Supply
            GST_Treatment = instance.GST_Treatment
            EmployeeID = instance.EmployeeID

            Action = "D"

            LogID = SalesEstimateMaster_Log.objects.create(
                CompanyID=CompanyID,

                TransactionID=SalesEstimateMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalTax=TotalTax,
                NetTotal=NetTotal,
                BillDiscAmt=BillDiscAmt,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                DeliveryDate=DeliveryDate,
                TotalGrossAmt=TotalGrossAmt,
                TotalDiscount=TotalDiscount,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                EmployeeID=EmployeeID
            )

            instance.delete()
            detail_instances = SalesEstimateDetails.objects.filter(CompanyID=CompanyID,
                                                                   SalesEstimateMasterID=SalesEstimateMasterID, BranchID=BranchID)
            for detail_instance in detail_instances:
                SalesEstimateDetailsID = detail_instance.SalesEstimateDetailsID
                BranchID = detail_instance.BranchID
                SalesEstimateMasterID = detail_instance.SalesEstimateMasterID
                ProductID = detail_instance.ProductID
                Qty = detail_instance.Qty
                FreeQty = detail_instance.FreeQty
                UnitPrice = detail_instance.UnitPrice
                RateWithTax = detail_instance.RateWithTax
                PriceListID = detail_instance.PriceListID
                DiscountPerc = detail_instance.DiscountPerc
                DiscountAmount = detail_instance.DiscountAmount
                GrossAmount = detail_instance.GrossAmount
                TaxableAmount = detail_instance.TaxableAmount
                VATPerc = detail_instance.VATPerc
                VATAmount = detail_instance.VATAmount
                SGSTPerc = detail_instance.SGSTPerc
                SGSTAmount = detail_instance.SGSTAmount
                CGSTPerc = detail_instance.CGSTPerc
                CGSTAmount = detail_instance.CGSTAmount
                IGSTPerc = detail_instance.IGSTPerc
                IGSTAmount = detail_instance.IGSTAmount
                NetAmount = detail_instance.NetAmount
                InclusivePrice = detail_instance.InclusivePrice
                BatchCode = detail_instance.BatchCode
                ProductTaxID = detail_instance.ProductTaxID
                Description = detail_instance.Description

                SalesEstimateDetails_Log.objects.create(
                    TransactionID=SalesEstimateDetailsID,
                    SalesEstimateMaster_LogID=LogID.pk,
                    BranchID=BranchID,
                    Action=Action,
                    SalesEstimateMasterID=SalesEstimateMasterID,
                    ProductID=ProductID,
                    Qty=Qty,
                    FreeQty=FreeQty,
                    UnitPrice=UnitPrice,
                    InclusivePrice=InclusivePrice,
                    RateWithTax=RateWithTax,
                    PriceListID=PriceListID,
                    DiscountPerc=DiscountPerc,
                    DiscountAmount=DiscountAmount,
                    GrossAmount=GrossAmount,
                    TaxableAmount=TaxableAmount,
                    VATPerc=VATPerc,
                    VATAmount=VATAmount,
                    SGSTPerc=SGSTPerc,
                    SGSTAmount=SGSTAmount,
                    CGSTPerc=CGSTPerc,
                    CGSTAmount=CGSTAmount,
                    IGSTPerc=IGSTPerc,
                    IGSTAmount=IGSTAmount,
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    BatchCode=BatchCode,
                    ProductTaxID=ProductTaxID,
                    Description=Description,
                )

                detail_instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Estimates',
                     'Delete', 'Sale Estimates Deleted successfully.', 'Sale Estimates Deleted successfully')

        response_data = {
            "StatusCode": 6000,
            "message": "Sales Estimate Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Estimate Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesEstimate_pagination(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']
    filterID = data['filterID']
    try:
        UserID = data["UserID"]
    except:
        UserID = 0
    try:
        EmployeeID = data["EmployeeID"]
    except:
        EmployeeID = 0

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if page_number and items_per_page:
            sale_object = SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if UserID > 0:
                sale_object = sale_object.filter(CreatedUserID=UserID)
            if EmployeeID > 0:
                sale_object = sale_object.filter(EmployeeID=EmployeeID)
                
            # is_data_exist = False
            # if filterID == "Pending":
            #     if sale_object.filter(IsInvoiced="N").exists():
            #         is_data_exist = True
            #         sale_object = sale_object.filter(IsInvoiced="N")
            # elif filterID == "Invoiced":
            #     if sale_object.filter(IsInvoiced="I").exists():
            #         is_data_exist = True
            #         sale_object = sale_object.filter(IsInvoiced="I")
            # elif filterID == "Cancelled":
            #     if sale_object.filter(IsInvoiced="C").exists():
            #         is_data_exist = True
            #         sale_object = sale_object.filter(IsInvoiced="C")
            # else:
            is_data_exist = True
            # sale_object = sale_object

            sale_sort_pagination = list_pagination(
                sale_object,
                items_per_page,
                page_number
            )
            sale_serializer = SalesEstimateMaster1RestSerializer(
                sale_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = sale_serializer.data
            if not data == None and is_data_exist == True:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(sale_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def cancel_salesEstimateMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    today = datetime.datetime.now()

    if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = SalesEstimateMaster.objects.get(CompanyID=CompanyID, pk=pk)
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Sales Estimate Cancelled Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Estimate Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_salesEstimate_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            ledger_ids = []
            if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=product_name).exists():
                ledgrs = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name)
                ledger_ids = ledgrs.values_list('LedgerID', flat=True)
            if length < 3:
                if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=product_name).exists():
                    ledgrs = AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=product_name)
                    ledger_ids = ledgrs.values_list('LedgerID', flat=True)[:10]
                instances = SalesEstimateMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(VoucherNo__icontains=product_name)) | (
                    Q(Date__icontains=product_name)) | (
                    Q(LedgerID__in=ledger_ids)))[:10]
            else:
                instances = SalesEstimateMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(VoucherNo__icontains=product_name)) | (
                    Q(Date__icontains=product_name)) | (
                    Q(LedgerID__in=ledger_ids)))
            serialized = SalesEstimateMaster1RestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, })

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
