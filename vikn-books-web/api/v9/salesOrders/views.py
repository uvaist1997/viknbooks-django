import datetime
import os
import sys

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.aggregates import Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v9.brands.serializers import ListSerializer
from api.v9.ledgerPosting.functions import convertOrderdDict
from api.v9.sales.functions import get_Genrate_VoucherNo
from api.v9.salesOrders.functions import get_auto_id, get_auto_idMaster
from api.v9.salesOrders.serializers import (
    SalesOrderMaster1RestSerializer,
    SalesOrderMasterRestSerializer,
    SalesOrderReportSerializer,
)
from brands.models import (
    AccountLedger,
    GeneralSettings,
    SalesEstimateMaster,
    SalesOrderDetails,
    SalesOrderDetails_Log,
    SalesOrderMaster,
    SalesOrderMaster_Log,
    SerialNumbers,
    UserAdrress,
)
from main.functions import activity_log, converted_float, get_LedgerBalance, get_company, update_voucher_table


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_salesOrder(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherNo = data["VoucherNo"]
            Date = data["Date"]
            DeliveryDate = data["DeliveryDate"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            TotalTax = data["TotalTax"]
            NetTotal = data["NetTotal"]
            BillDiscAmt = data["BillDiscAmt"]
            BillDiscPercent = data["BillDiscPercent"]
            GrandTotal = data["GrandTotal"]
            RoundOff = data["RoundOff"]
            IsActive = data["IsActive"]
            IsInvoiced = data["IsInvoiced"]
            TaxID = data["TaxID"]
            TaxType = data["TaxType"]
            VATAmount = data["VATAmount"]
            SGSTAmount = data["SGSTAmount"]
            CGSTAmount = data["CGSTAmount"]
            IGSTAmount = data["IGSTAmount"]
            TAX1Amount = data["TAX1Amount"]
            TAX2Amount = data["TAX2Amount"]
            TAX3Amount = data["TAX3Amount"]

            Action = "A"

            try:
                ShippingCharge = data["ShippingCharge"]
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data["shipping_tax_amount"]
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data["TaxTypeID"]
            except:
                TaxTypeID = ""

            try:
                SAC = data["SAC"]
            except:
                SAC = ""

            try:
                SalesTax = data["SalesTax"]
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            try:
                ShippingAddress = data["ShippingAddress"]
            except:
                ShippingAddress = None
            
            TotalDiscount = converted_float(data["TotalDiscount"])

            if ShippingAddress:
                if UserAdrress.objects.filter(id=ShippingAddress).exists():
                    ShippingAddress = UserAdrress.objects.get(id=ShippingAddress)

            VoucherType = "SO"

            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "SO"

            try:
                Seperator = data["Seperator"]
            except:
                Seperator = ""

            try:
                InvoiceNo = data["InvoiceNo"]
            except:
                InvoiceNo = 1

            try:
                TotalGrossAmt = data["TotalGrossAmt"]
            except:
                TotalGrossAmt = 0

            try:
                EstimateNo = data["EstimateNo"]
            except:
                EstimateNo = "SE0"

            try:
                estimate_vouchers = data["estimate_vouchers"]
            except:
                estimate_vouchers = []
                
            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None

            if BillingAddress:
                if UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = UserAdrress.objects.get(
                        id=BillingAddress)

            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0

            if SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherNo=EstimateNo, Status="N"
            ).exists():
                estimate_instance = SalesEstimateMaster.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    VoucherNo=EstimateNo,
                    Status="N",
                )
                estimate_instance.Status = "O"
                estimate_instance.save()
            else:
                if estimate_vouchers:
                    estimate_instances = SalesEstimateMaster.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        VoucherNo__in=estimate_vouchers,
                        Status="N",
                    )
                    for b in estimate_instances:
                        b.Status = "O"
                        b.save()

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOrderOK = True

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="VoucherNoAutoGenerate",
            ).exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                    SettingsType="VoucherNoAutoGenerate",
                ).SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesOrderMaster, BranchID, CompanyID, "SO"
                )
                is_SaleOrderOK = True
            elif is_voucherExist == False:
                is_SaleOrderOK = True
            else:
                is_SaleOrderOK = False

            if is_SaleOrderOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
                )
                SalesOrderMasterID = get_auto_idMaster(
                    SalesOrderMaster, BranchID, CompanyID
                )

                SalesOrderMaster_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=SalesOrderMasterID,
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
                    IsInvoiced=IsInvoiced,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    TotalGrossAmt=TotalGrossAmt,
                    ShippingAddress=ShippingAddress,
                    EstimateNo=EstimateNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    BillingAddress=BillingAddress,
                )

                SalesOrderMaster.objects.create(
                    CompanyID=CompanyID,
                    SalesOrderMasterID=SalesOrderMasterID,
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
                    IsInvoiced=IsInvoiced,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    TotalGrossAmt=TotalGrossAmt,
                    ShippingAddress=ShippingAddress,
                    EstimateNo=EstimateNo,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    BillingAddress=BillingAddress,
                )

                saleOrdersDetails = data["saleOrdersDetails"]

                for saleOrdersDetail in saleOrdersDetails:
                    ProductID = saleOrdersDetail["ProductID"]
                    if ProductID:
                        Qty = saleOrdersDetail["Qty"]
                        FreeQty = saleOrdersDetail["FreeQty"]
                        UnitPrice = saleOrdersDetail["UnitPrice"]
                        RateWithTax = saleOrdersDetail["RateWithTax"]
                        PriceListID = saleOrdersDetail["PriceListID"]
                        DiscountPerc = saleOrdersDetail["DiscountPerc"]
                        DiscountAmount = saleOrdersDetail["DiscountAmount"]
                        GrossAmount = saleOrdersDetail["GrossAmount"]
                        TaxableAmount = saleOrdersDetail["TaxableAmount"]
                        VATPerc = saleOrdersDetail["VATPerc"]
                        VATAmount = saleOrdersDetail["VATAmount"]
                        SGSTPerc = saleOrdersDetail["SGSTPerc"]
                        SGSTAmount = saleOrdersDetail["SGSTAmount"]
                        CGSTPerc = saleOrdersDetail["CGSTPerc"]
                        CGSTAmount = saleOrdersDetail["CGSTAmount"]
                        IGSTPerc = saleOrdersDetail["IGSTPerc"]
                        IGSTAmount = saleOrdersDetail["IGSTAmount"]
                        TAX1Perc = saleOrdersDetail["TAX1Perc"]
                        TAX1Amount = saleOrdersDetail["TAX1Amount"]
                        TAX2Perc = saleOrdersDetail["TAX2Perc"]
                        TAX2Amount = saleOrdersDetail["TAX2Amount"]
                        TAX3Perc = saleOrdersDetail["TAX3Perc"]
                        TAX3Amount = saleOrdersDetail["TAX3Amount"]
                        try:
                            KFCAmount = saleOrdersDetail["KFCAmount"]
                        except:
                            KFCAmount = 0

                        NetAmount = saleOrdersDetail["NetAmount"]
                        InclusivePrice = saleOrdersDetail["InclusivePrice"]
                        BatchCode = saleOrdersDetail["BatchCode"]

                        try:
                            SerialNos = saleOrdersDetail["SerialNos"]
                        except:
                            SerialNos = []

                        try:
                            Description = saleOrdersDetail["Description"]
                        except:
                            Description = ""

                        try:
                            ProductTaxID = saleOrdersDetail["ProductTaxID"]
                        except:
                            ProductTaxID = ""

                        SalesOrderDetailsID = get_auto_id(
                            SalesOrderDetails, BranchID, CompanyID
                        )

                        if SerialNos:
                            for sn in SerialNos:
                                try:
                                    SerialNo = sn["SerialNo"]
                                except:
                                    SerialNo = ""
                                try:
                                    ItemCode = sn["ItemCode"]
                                except:
                                    ItemCode = ""
                                SerialNumbers.objects.create(
                                    VoucherType="SO",
                                    CompanyID=CompanyID,
                                    SerialNo=SerialNo,
                                    ItemCode=ItemCode,
                                    SalesMasterID=SalesOrderMasterID,
                                    SalesDetailsID=SalesOrderDetailsID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
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
                            UpdatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                        SalesOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesOrderDetailsID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
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
                            UpdatedUserID=CreatedUserID,
                            InclusivePrice=InclusivePrice,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')
                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "StatusCode": 6000,
                    "message": "Sale Orders created Successfully!!!",
                    "CashBalance": cash_Balance,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Sale Orders",
                    "Create",
                    "Sale Orders created Failed.",
                    "VoucherNo already exist!",
                )
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales Order",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_salesOrder(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            salesOrderMaster_instance = None
            salesOrderDetails = None

            salesOrderMaster_instance = SalesOrderMaster.objects.get(
                CompanyID=CompanyID, pk=pk
            )

            SalesOrderMasterID = salesOrderMaster_instance.SalesOrderMasterID
            BranchID = salesOrderMaster_instance.BranchID
            VoucherNo = salesOrderMaster_instance.VoucherNo

            Date = data["Date"]
            DeliveryDate = data["DeliveryDate"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            TotalTax = data["TotalTax"]
            NetTotal = data["NetTotal"]
            BillDiscAmt = data["BillDiscAmt"]
            BillDiscPercent = data["BillDiscPercent"]
            GrandTotal = data["GrandTotal"]
            RoundOff = data["RoundOff"]
            IsActive = data["IsActive"]
            IsInvoiced = data["IsInvoiced"]
            TaxID = data["TaxID"]
            TaxType = data["TaxType"]
            VATAmount = data["VATAmount"]
            SGSTAmount = data["SGSTAmount"]
            CGSTAmount = data["CGSTAmount"]
            IGSTAmount = data["IGSTAmount"]
            TAX1Amount = data["TAX1Amount"]
            TAX2Amount = data["TAX2Amount"]
            TAX3Amount = data["TAX3Amount"]

            Action = "M"

            try:
                ShippingCharge = data["ShippingCharge"]
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data["shipping_tax_amount"]
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data["TaxTypeID"]
            except:
                TaxTypeID = ""

            try:
                SAC = data["SAC"]
            except:
                SAC = ""

            try:
                SalesTax = data["SalesTax"]
            except:
                SalesTax = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            try:
                EstimateNo = data["EstimateNo"]
            except:
                EstimateNo = ""

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
            
            TotalDiscount = converted_float(data["TotalDiscount"])

            SalesOrderMaster_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=SalesOrderMasterID,
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
                IsInvoiced=IsInvoiced,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                TaxID=TaxID,
                TaxType=TaxType,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                ShippingCharge=ShippingCharge,
                shipping_tax_amount=shipping_tax_amount,
                TaxTypeID=TaxTypeID,
                SAC=SAC,
                SalesTax=SalesTax,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                VAT_Treatment=VAT_Treatment,
                EstimateNo=EstimateNo,
                TaxTaxableAmount=TaxTaxableAmount,
                NonTaxTaxableAmount=NonTaxTaxableAmount,
                TotalDiscount=TotalDiscount,
                BillingAddress=BillingAddress,
            )
            if SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                SalesMasterID=SalesOrderMasterID,
                BranchID=BranchID,
                VoucherType="SO",
            ).exists():
                SerialNumbersInstances = SerialNumbers.objects.filter(
                    CompanyID=CompanyID,
                    SalesMasterID=SalesOrderMasterID,
                    BranchID=BranchID,
                    VoucherType="SO",
                )
                for sli in SerialNumbersInstances:
                    sli.delete()

            salesOrderMaster_instance.Date = Date
            salesOrderMaster_instance.DeliveryDate = DeliveryDate
            salesOrderMaster_instance.LedgerID = LedgerID
            salesOrderMaster_instance.PriceCategoryID = PriceCategoryID
            salesOrderMaster_instance.CustomerName = CustomerName
            salesOrderMaster_instance.Address1 = Address1
            salesOrderMaster_instance.Address2 = Address2
            salesOrderMaster_instance.Notes = Notes
            salesOrderMaster_instance.FinacialYearID = FinacialYearID
            salesOrderMaster_instance.TotalTax = TotalTax
            salesOrderMaster_instance.NetTotal = NetTotal
            salesOrderMaster_instance.BillDiscAmt = BillDiscAmt
            salesOrderMaster_instance.BillDiscPercent = BillDiscPercent
            salesOrderMaster_instance.GrandTotal = GrandTotal
            salesOrderMaster_instance.RoundOff = RoundOff
            salesOrderMaster_instance.IsActive = IsActive
            salesOrderMaster_instance.IsInvoiced = IsInvoiced
            salesOrderMaster_instance.Action = Action
            salesOrderMaster_instance.UpdatedDate = today
            salesOrderMaster_instance.UpdatedUserID = CreatedUserID
            salesOrderMaster_instance.TaxID = TaxID
            salesOrderMaster_instance.TaxType = TaxType
            salesOrderMaster_instance.CompanyID = CompanyID
            salesOrderMaster_instance.VATAmount = VATAmount
            salesOrderMaster_instance.SGSTAmount = SGSTAmount
            salesOrderMaster_instance.CGSTAmount = CGSTAmount
            salesOrderMaster_instance.IGSTAmount = IGSTAmount
            salesOrderMaster_instance.TAX1Amount = TAX1Amount
            salesOrderMaster_instance.TAX2Amount = TAX2Amount
            salesOrderMaster_instance.TAX3Amount = TAX3Amount
            salesOrderMaster_instance.ShippingCharge = ShippingCharge
            salesOrderMaster_instance.shipping_tax_amount = shipping_tax_amount
            salesOrderMaster_instance.TaxTypeID = TaxTypeID
            salesOrderMaster_instance.SAC = SAC
            salesOrderMaster_instance.SalesTax = SalesTax
            salesOrderMaster_instance.Country_of_Supply = Country_of_Supply
            salesOrderMaster_instance.State_of_Supply = State_of_Supply
            salesOrderMaster_instance.GST_Treatment = GST_Treatment
            salesOrderMaster_instance.VAT_Treatment = VAT_Treatment
            salesOrderMaster_instance.EstimateNo = EstimateNo

            salesOrderMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesOrderMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            salesOrderMaster_instance.TotalDiscount = TotalDiscount
            salesOrderMaster_instance.BillingAddress = BillingAddress
            salesOrderMaster_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]

                    if not deleted_pk == "" or not deleted_pk == 0:
                        if SalesOrderDetails.objects.filter(
                            CompanyID=CompanyID, pk=deleted_pk
                        ).exists():
                            deleted_detail = SalesOrderDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            )
                            deleted_detail.delete()

            salesOrderDetails = data["saleOrdersDetails"]
            for salesOrderDetail in salesOrderDetails:

                unq_id = salesOrderDetail["unq_id"]
                ProductID = salesOrderDetail["ProductID"]
                if ProductID:
                    Qty = salesOrderDetail["Qty"]
                    FreeQty = salesOrderDetail["FreeQty"]
                    UnitPrice = salesOrderDetail["UnitPrice"]
                    RateWithTax = salesOrderDetail["RateWithTax"]
                    PriceListID = salesOrderDetail["PriceListID"]
                    DiscountPerc = salesOrderDetail["DiscountPerc"]
                    DiscountAmount = salesOrderDetail["DiscountAmount"]
                    GrossAmount = salesOrderDetail["GrossAmount"]
                    TaxableAmount = salesOrderDetail["TaxableAmount"]
                    VATPerc = salesOrderDetail["VATPerc"]
                    VATAmount = salesOrderDetail["VATAmount"]
                    SGSTPerc = salesOrderDetail["SGSTPerc"]
                    SGSTAmount = salesOrderDetail["SGSTAmount"]
                    CGSTPerc = salesOrderDetail["CGSTPerc"]
                    CGSTAmount = salesOrderDetail["CGSTAmount"]
                    IGSTPerc = salesOrderDetail["IGSTPerc"]
                    IGSTAmount = salesOrderDetail["IGSTAmount"]
                    TAX1Perc = salesOrderDetail["TAX1Perc"]
                    TAX1Amount = salesOrderDetail["TAX1Amount"]
                    TAX2Perc = salesOrderDetail["TAX2Perc"]
                    TAX2Amount = salesOrderDetail["TAX2Amount"]
                    TAX3Perc = salesOrderDetail["TAX3Perc"]
                    TAX3Amount = salesOrderDetail["TAX3Amount"]
                    KFCAmount = salesOrderDetail["KFCAmount"]
                    NetAmount = salesOrderDetail["NetAmount"]
                    BatchCode = salesOrderDetail["BatchCode"]
                    InclusivePrice = salesOrderDetail["InclusivePrice"]
                    detailID = salesOrderDetail["detailID"]

                    try:
                        SerialNos = salesOrderDetail["SerialNos"]
                    except:
                        SerialNos = []

                    try:
                        Description = salesOrderDetail["Description"]
                    except:
                        Description = ""

                    try:
                        ProductTaxID = salesOrderDetail["ProductTaxID"]
                    except:
                        ProductTaxID = ""
                        
                    try:
                        Description = salesOrderDetail["Description"]
                    except:
                        Description = ""

                    if detailID == 0:
                        Action = "M"
                        salesDetail_instance = SalesOrderDetails.objects.get(
                            CompanyID=CompanyID, pk=unq_id
                        )
                        SalesOrderDetailsID = salesDetail_instance.SalesOrderDetailsID

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
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
                            UpdatedUserID=CreatedUserID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

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
                        salesDetail_instance.UpdatedUserID = CreatedUserID
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
                        salesDetail_instance.LogID = log_instance.ID
                        salesDetail_instance.ProductTaxID = log_instance.ProductTaxID
                        salesDetail_instance.Description = Description
                        salesDetail_instance.save()

                    if detailID == 1:
                        SalesOrderDetailsID = get_auto_id(
                            SalesOrderDetails, BranchID, CompanyID
                        )
                        Action = "A"

                        log_instance = SalesOrderDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
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
                            UpdatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                        SalesOrderDetails.objects.create(
                            CompanyID=CompanyID,
                            SalesOrderDetailsID=SalesOrderDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesOrderMasterID=SalesOrderMasterID,
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
                            UpdatedUserID=CreatedUserID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID,
                            Description=Description
                        )

                    # ======
                    if SerialNos:
                        for sn in SerialNos:
                            try:
                                SerialNo = sn["SerialNo"]
                            except:
                                SerialNo = ""
                            try:
                                ItemCode = sn["ItemCode"]
                            except:
                                ItemCode = ""

                            SerialNumbers.objects.create(
                                CompanyID=CompanyID,
                                VoucherType="SO",
                                SerialNo=SerialNo,
                                ItemCode=ItemCode,
                                SalesMasterID=SalesOrderMasterID,
                                SalesDetailsID=SalesOrderDetailsID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )
                    # ======
                    print(
                        SerialNos,
                        "PPPPPPPPPPPPPPPP*************************PPPPPPPPPPPPPPPPPPP",
                    )

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
            #              'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')
            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "SalesOrder Updated Successfully!!!",
                "CashBalance": cash_Balance,
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
        }

        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales Order",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_salesOrderMaster(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    filterID = data["filterID"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data["BranchID"]
        if SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            instances = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            is_data_exist = False
            if filterID == "Pending":
                if instances.filter(IsInvoiced="N").exists():
                    is_data_exist = True
                    instances = instances.filter(IsInvoiced="N")
            elif filterID == "Invoiced":
                if instances.filter(IsInvoiced="I").exists():
                    is_data_exist = True
                    instances = instances.filter(IsInvoiced="I")
            elif filterID == "Cancelled":
                if instances.filter(IsInvoiced="C").exists():
                    is_data_exist = True
                    instances = instances.filter(IsInvoiced="C")
            else:
                is_data_exist = True
                instances = instances

            serialized = SalesOrderMasterRestSerializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )

            if is_data_exist == True:
                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                #              'List', 'Sale Orders List viewed successfully.', 'Sale Orders List viewed successfully')

                response_data = {"StatusCode": 6000, "data": serialized.data}

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Sales Order Not Found!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": "Sales Order Not Found!"}

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesOrderMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SalesOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding}
        )

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'View',
        #              'Sale Orders Single viewed successfully.', 'Sale Orders Single viewed successfully')
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Sales Order Master Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_salesOrderMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instance = None
    if selecte_ids:
        if SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = SalesOrderMaster.objects.filter(pk__in=selecte_ids)
    else:
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = SalesOrderMaster.objects.filter(pk=pk)

    # if SalesOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
    #     instance = SalesOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
    if instances:
        for instance in instances:
            SalesOrderMasterID = instance.SalesOrderMasterID
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
            # BillDiscount = instance.BillDiscount
            GrandTotal = instance.GrandTotal
            RoundOff = instance.RoundOff
            IsActive = instance.IsActive
            DeliveryDate = instance.DeliveryDate
            IsInvoiced = instance.IsInvoiced
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

            Action = "D"

            SalesOrderMaster_Log.objects.create(
                CompanyID=CompanyID,
                TransactionID=SalesOrderMasterID,
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
                # BillDiscount=BillDiscount,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                IsActive=IsActive,
                IsInvoiced=IsInvoiced,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                DeliveryDate=DeliveryDate,
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
            )

            instance.delete()

            detail_instances = SalesOrderDetails.objects.filter(
                CompanyID=CompanyID,
                SalesOrderMasterID=SalesOrderMasterID,
                BranchID=BranchID,
            )

            for detail_instance in detail_instances:
                SalesOrderDetailsID = detail_instance.SalesOrderDetailsID
                BranchID = detail_instance.BranchID
                SalesOrderMasterID = detail_instance.SalesOrderMasterID
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

                SalesOrderDetails_Log.objects.create(
                    TransactionID=SalesOrderDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    SalesOrderMasterID=SalesOrderMasterID,
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
                    UpdatedUserID=CreatedUserID,
                    BatchCode=BatchCode,
                    ProductTaxID=ProductTaxID,
                    Description=Description
                )

                detail_instance.delete()

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Sale Orders",
            "Delete",
            "Sale Orders Deleted successfully.",
            "Sale Orders Deleted successfully",
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Sales Order Master Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "Sales Order Master Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesOrder_pagination(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]
    filterID = data["filterID"]

    try:
        is_filter = data["is_filter"]
    except:
        is_filter = False

    try:
        is_pending = data["is_pending"]
    except:
        is_pending = False

    try:
        is_invoiced = data["is_invoiced"]
    except:
        is_invoiced = False

    try:
        is_cancelled = data["is_cancelled"]
    except:
        is_cancelled = False

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]

        if page_number and items_per_page:
            sale_object = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )

            is_data_exist = False
            if is_filter == True:
                is_invoicedList = []
                if is_pending:
                    is_invoicedList.append("N")
                if is_invoiced:
                    is_invoicedList.append("I")
                if is_cancelled:
                    is_invoicedList.append("C")
                sale_object = sale_object.filter(IsInvoiced__in=is_invoicedList)
                if sale_object:
                    is_data_exist = True
            else:
                if filterID == "Pending":
                    if sale_object.filter(IsInvoiced="N").exists():
                        is_data_exist = True
                        sale_object = sale_object.filter(IsInvoiced="N")
                elif filterID == "Invoiced":
                    if sale_object.filter(IsInvoiced="I").exists():
                        is_data_exist = True
                        sale_object = sale_object.filter(IsInvoiced="I")
                elif filterID == "Cancelled":
                    if sale_object.filter(IsInvoiced="C").exists():
                        is_data_exist = True
                        sale_object = sale_object.filter(IsInvoiced="C")
                else:
                    is_data_exist = True
                    sale_object = sale_object

            sale_sort_pagination = list_pagination(
                sale_object, items_per_page, page_number
            )
            sale_serializer = SalesOrderMaster1RestSerializer(
                sale_sort_pagination,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = sale_serializer.data
            if not data == None and is_data_exist == True:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(sale_object),
                }
            else:
                response_data = {"StatusCode": 6001}

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def cancel_salesOrderMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    BranchID = data["BranchID"]
    today = datetime.datetime.now()

    if SalesOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = SalesOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
        instance.IsInvoiced = "C"
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Sales Order Cancelled Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "Sales Order Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_salesOrder(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    PriceRounding = data["PriceRounding"]
    FromDate = data["FromDate"]
    ToDate = data["ToDate"]
    ReportTypes = data["ReportTypes"]
    print("---------------------------------------")
    print(ReportTypes)
    print(CompanyID)
    print(BranchID)
    print(FromDate)
    print(ToDate)
    test = SalesOrderMaster.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        Date__gte=FromDate,
        Date__lte=ToDate,
        IsInvoiced__in=ReportTypes,
    )
    print(test)
    if SalesOrderMaster.objects.filter(
        CompanyID=CompanyID,
        BranchID=BranchID,
        Date__gte=FromDate,
        Date__lte=ToDate,
        IsInvoiced__in=ReportTypes,
    ).exists():
        instance = SalesOrderMaster.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            Date__gte=FromDate,
            Date__lte=ToDate,
            IsInvoiced__in=ReportTypes,
        )

        serialized = SalesOrderReportSerializer(
            instance,
            many=True,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
            },
        )
        jsnDatas = convertOrderdDict(serialized.data)
        TotalTax = instance.aggregate(Sum("TotalTax"))["TotalTax__sum"]
        NetTotal = instance.aggregate(Sum("NetTotal"))["NetTotal__sum"]
        GrandTotal = instance.aggregate(Sum("GrandTotal"))["GrandTotal__sum"]

        total_dic = {
            "LedgerName": "Total",
            "TotalTax": TotalTax,
            "NetTotal": NetTotal,
            "GrandTotal": GrandTotal,
        }
        jsnDatas.append(total_dic)
        response_data = {"StatusCode": 6000, "data": jsnDatas}
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Datas Not Found During this time!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_salesOrder_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            ledger_ids = []
            if AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=product_name
            ).exists():
                ledgrs = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name
                )
                ledger_ids = ledgrs.values_list("LedgerID", flat=True)
            if length < 3:
                if AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name
                ).exists():
                    ledgrs = AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=product_name
                    )
                    ledger_ids = ledgrs.values_list("LedgerID", flat=True)[:10]
                instances = SalesOrderMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(VoucherNo__icontains=product_name))
                    | (Q(Date__icontains=product_name))
                    | (Q(LedgerID__in=ledger_ids))
                )[:10]
            else:
                instances = SalesOrderMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(VoucherNo__icontains=product_name))
                    | (Q(Date__icontains=product_name))
                    | (Q(LedgerID__in=ledger_ids))
                )
            serialized = SalesOrderMaster1RestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
