from brands.models import PurchaseOrderMaster, PurchaseOrderMaster_Log, PurchaseOrderDetails, PurchaseOrderDetails_Log, PurchaseOrderDetailsDummy, GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.purchaseOrders.serializers import PurchaseOrderMasterSerializer, PurchaseOrderMasterRestSerializer, PurchaseOrderDetailsSerializer, PurchaseOrderDetailsRestSerializer,PurchaseOrderReportSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.purchaseOrders.functions import generate_serializer_errors
from rest_framework import status
from api.v4.purchaseOrders.functions import get_auto_id, get_auto_idMaster
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v4.sales.functions import get_Genrate_VoucherNo


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
def create_purchaseOrder(request):
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
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    IsActive = data['IsActive']
    IsInvoiced = data['IsInvoiced']
    TaxID = data['TaxID']
    TaxType = data['TaxType']
    VATAmount = data['VATAmount']
    SGSTAmount = data['SGSTAmount']
    CGSTAmount = data['CGSTAmount']
    IGSTAmount = data['IGSTAmount']
    TAX1Amount = data['TAX1Amount']
    TAX2Amount = data['TAX2Amount']
    TAX3Amount = data['TAX3Amount']

    Action = "A"

    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = PurchaseOrderMaster.objects.filter(BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    check_VoucherNoAutoGenerate = False
    is_PurchaseOrderOK = True

    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
        check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

    if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
        VoucherNo = get_Genrate_VoucherNo(
            PurchaseOrderMaster, BranchID, CompanyID, "PO")
        is_PurchaseOrderOK = True
    elif is_voucherExist == False:
        is_PurchaseOrderOK = True
    else:
        is_PurchaseOrderOK = False

    if is_PurchaseOrderOK:

        PurchaseOrderMasterID = get_auto_idMaster(
            PurchaseOrderMaster, BranchID, CompanyID)

        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            CompanyID=CompanyID,
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
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            IsInvoiced=IsInvoiced,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            TaxID=TaxID,
            TaxType=TaxType,
        )

        PurchaseOrderMaster.objects.create(
            CompanyID=CompanyID,
            PurchaseOrderMasterID=PurchaseOrderMasterID,
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
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            IsInvoiced=IsInvoiced,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            TaxID=TaxID,
            TaxType=TaxType,
        )

        purchaseOrderDetails = data["PurchaseOrderDetails"]

        for purchaseOrderDetail in purchaseOrderDetails:

            ProductID = purchaseOrderDetail['ProductID']
            Qty = purchaseOrderDetail['Qty']
            FreeQty = purchaseOrderDetail['FreeQty']
            UnitPrice = purchaseOrderDetail['UnitPrice']
            RateWithTax = purchaseOrderDetail['RateWithTax']
            CostPerItem = purchaseOrderDetail['CostPerItem']
            PriceListID = purchaseOrderDetail['PriceListID']
            # TaxID = purchaseOrderDetail['TaxID']
            # TaxType = purchaseOrderDetail['TaxType']
            DiscountPerc = purchaseOrderDetail['DiscountPerc']
            DiscountAmount = purchaseOrderDetail['DiscountAmount']
            GrossAmount = purchaseOrderDetail['GrossAmount']
            TaxableAmount = purchaseOrderDetail['TaxableAmount']
            VATPerc = purchaseOrderDetail['VATPerc']
            VATAmount = purchaseOrderDetail['VATAmount']
            SGSTPerc = purchaseOrderDetail['SGSTPerc']
            SGSTAmount = purchaseOrderDetail['SGSTAmount']
            CGSTPerc = purchaseOrderDetail['CGSTPerc']
            CGSTAmount = purchaseOrderDetail['CGSTAmount']
            IGSTPerc = purchaseOrderDetail['IGSTPerc']
            IGSTAmount = purchaseOrderDetail['IGSTAmount']
            NetAmount = purchaseOrderDetail['NetAmount']
            TAX1Perc = purchaseOrderDetail['TAX1Perc']
            TAX1Amount = purchaseOrderDetail['TAX1Amount']
            TAX2Perc = purchaseOrderDetail['TAX2Perc']
            TAX2Amount = purchaseOrderDetail['TAX2Amount']
            TAX3Perc = purchaseOrderDetail['TAX3Perc']
            TAX3Amount = purchaseOrderDetail['TAX3Amount']
            NetAmount = purchaseOrderDetail['NetAmount']
            InclusivePrice = purchaseOrderDetail['InclusivePrice']
            BatchCode = purchaseOrderDetail['BatchCode']

            PurchaseOrderDetailsID = get_auto_id(
                PurchaseOrderDetails, BranchID, CompanyID)

            log_instance = PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                CompanyID=CompanyID,
                BranchID=BranchID,
                Action=Action,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                InclusivePrice=InclusivePrice,
                BatchCode=BatchCode,
                CostPerItem=CostPerItem
            )

            PurchaseOrderDetails.objects.create(
                CompanyID=CompanyID,
                PurchaseOrderDetailsID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                InclusivePrice=InclusivePrice,
                BatchCode=BatchCode,
                LogID=log_instance.ID,
                CostPerItem=CostPerItem
            )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder',
                     'Create', 'Purchase Order created successfully.', 'Purchase Order created successfully')

        response_data = {
            "StatusCode": 6000,
            "message": "Purchase Order  created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseOrder',
                     'Create', 'Purchase Order created Failed.', 'VoucherNo already exist!')
        response_data = {
            "StatusCode": 6001,
            "message": "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_purchaseOrder(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()

    purchaseOrderMaster_instance = PurchaseOrderMaster.objects.get(
        CompanyID=CompanyID, pk=pk)

    PurchaseOrderMasterID = purchaseOrderMaster_instance.PurchaseOrderMasterID
    BranchID = purchaseOrderMaster_instance.BranchID
    VoucherNo = purchaseOrderMaster_instance.VoucherNo

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
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    IsActive = data['IsActive']
    IsInvoiced = data['IsInvoiced']
    TaxID = data['TaxID']
    TaxType = data['TaxType']
    VATAmount = data['VATAmount']
    SGSTAmount = data['SGSTAmount']
    CGSTAmount = data['CGSTAmount']
    IGSTAmount = data['IGSTAmount']
    TAX1Amount = data['TAX1Amount']
    TAX2Amount = data['TAX2Amount']
    TAX3Amount = data['TAX3Amount']

    Action = "M"

    PurchaseOrderMaster_Log.objects.create(
        TransactionID=PurchaseOrderMasterID,
        CompanyID=CompanyID,
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
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        IsActive=IsActive,
        CreatedDate=today,
        UpdatedDate=today,
        CreatedUserID=CreatedUserID,
        IsInvoiced=IsInvoiced,
        VATAmount=VATAmount,
        SGSTAmount=SGSTAmount,
        CGSTAmount=CGSTAmount,
        IGSTAmount=IGSTAmount,
        TAX1Amount=TAX1Amount,
        TAX2Amount=TAX2Amount,
        TAX3Amount=TAX3Amount,
        TaxID=TaxID,
        TaxType=TaxType,
    )

    purchaseOrderMaster_instance.Date = Date
    purchaseOrderMaster_instance.DeliveryDate = DeliveryDate
    purchaseOrderMaster_instance.LedgerID = LedgerID
    purchaseOrderMaster_instance.PriceCategoryID = PriceCategoryID
    purchaseOrderMaster_instance.CustomerName = CustomerName
    purchaseOrderMaster_instance.Address1 = Address1
    purchaseOrderMaster_instance.Address2 = Address2
    purchaseOrderMaster_instance.Notes = Notes
    purchaseOrderMaster_instance.FinacialYearID = FinacialYearID
    purchaseOrderMaster_instance.TotalTax = TotalTax
    purchaseOrderMaster_instance.NetTotal = NetTotal
    purchaseOrderMaster_instance.GrandTotal = GrandTotal
    purchaseOrderMaster_instance.RoundOff = RoundOff
    purchaseOrderMaster_instance.IsActive = IsActive
    purchaseOrderMaster_instance.IsInvoiced = IsInvoiced
    purchaseOrderMaster_instance.TaxID = TaxID
    purchaseOrderMaster_instance.TaxType = TaxType
    purchaseOrderMaster_instance.VATAmount = VATAmount
    purchaseOrderMaster_instance.SGSTAmount = SGSTAmount
    purchaseOrderMaster_instance.CGSTAmount = CGSTAmount
    purchaseOrderMaster_instance.IGSTAmount = IGSTAmount
    purchaseOrderMaster_instance.TAX1Amount = TAX1Amount
    purchaseOrderMaster_instance.TAX2Amount = TAX2Amount
    purchaseOrderMaster_instance.TAX3Amount = TAX3Amount
    purchaseOrderMaster_instance.save()

    

    deleted_datas = data["deleted_data"]
    if deleted_datas:
        for deleted_Data in deleted_datas:
            deleted_pk = deleted_Data['unq_id']

            if not deleted_pk == '' or not deleted_pk == 0:
                if PurchaseOrderDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                    deleted_detail = PurchaseOrderDetails.objects.filter(
                        CompanyID=CompanyID, pk=deleted_pk)
                    deleted_detail.delete()

    purchaseOrderDetails = data["purchaseOrdersDetails"]
    for purchaseOrderDetail in purchaseOrderDetails:
        unq_id = purchaseOrderDetail['unq_id']
        ProductID = purchaseOrderDetail['ProductID']
        if ProductID:
            Qty = purchaseOrderDetail['Qty']
            FreeQty = purchaseOrderDetail['FreeQty']
            UnitPrice = purchaseOrderDetail['UnitPrice']
            RateWithTax = purchaseOrderDetail['RateWithTax']
            CostPerItem = purchaseOrderDetail['CostPerItem']
            PriceListID = purchaseOrderDetail['PriceListID']
            DiscountPerc = purchaseOrderDetail['DiscountPerc']
            DiscountAmount = purchaseOrderDetail['DiscountAmount']
            GrossAmount = purchaseOrderDetail['GrossAmount']
            TaxableAmount = purchaseOrderDetail['TaxableAmount']
            VATPerc = purchaseOrderDetail['VATPerc']
            VATAmount = purchaseOrderDetail['VATAmount']
            SGSTPerc = purchaseOrderDetail['SGSTPerc']
            SGSTAmount = purchaseOrderDetail['SGSTAmount']
            CGSTPerc = purchaseOrderDetail['CGSTPerc']
            CGSTAmount = purchaseOrderDetail['CGSTAmount']
            IGSTPerc = purchaseOrderDetail['IGSTPerc']
            IGSTAmount = purchaseOrderDetail['IGSTAmount']
            NetAmount = purchaseOrderDetail['NetAmount']
            TAX1Perc = purchaseOrderDetail['TAX1Perc']
            TAX1Amount = purchaseOrderDetail['TAX1Amount']
            TAX2Perc = purchaseOrderDetail['TAX2Perc']
            TAX2Amount = purchaseOrderDetail['TAX2Amount']
            TAX3Perc = purchaseOrderDetail['TAX3Perc']
            TAX3Amount = purchaseOrderDetail['TAX3Amount']
            NetAmount = purchaseOrderDetail['NetAmount']
            InclusivePrice = purchaseOrderDetail['InclusivePrice']
            BatchCode = purchaseOrderDetail['BatchCode']
            detailID = purchaseOrderDetail['detailID']

            if detailID == 0:
                Action = "M"
                purchaseDetail_instance = PurchaseOrderDetails.objects.get(
                    CompanyID=CompanyID, pk=unq_id)
                PurchaseOrderDetailsID = purchaseDetail_instance.PurchaseOrderDetailsID

                log_instance = PurchaseOrderDetails_Log.objects.create(
                    TransactionID=PurchaseOrderDetailsID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    InclusivePrice=InclusivePrice,
                    BatchCode=BatchCode,
                    CostPerItem=CostPerItem
                )
                purchaseDetail_instance.ProductID = ProductID
                purchaseDetail_instance.Qty = Qty
                purchaseDetail_instance.FreeQty = FreeQty
                purchaseDetail_instance.UnitPrice = UnitPrice
                purchaseDetail_instance.RateWithTax = RateWithTax
                purchaseDetail_instance.CostPerItem = CostPerItem
                purchaseDetail_instance.PriceListID = PriceListID
                purchaseDetail_instance.DiscountPerc = DiscountPerc
                purchaseDetail_instance.DiscountAmount = DiscountAmount
                purchaseDetail_instance.GrossAmount = GrossAmount
                purchaseDetail_instance.TaxableAmount = TaxableAmount
                purchaseDetail_instance.VATPerc = VATPerc
                purchaseDetail_instance.VATAmount = VATAmount
                purchaseDetail_instance.SGSTPerc = SGSTPerc
                purchaseDetail_instance.SGSTAmount = SGSTAmount
                purchaseDetail_instance.CGSTPerc = CGSTPerc
                purchaseDetail_instance.CGSTAmount = CGSTAmount
                purchaseDetail_instance.IGSTPerc = IGSTPerc
                purchaseDetail_instance.IGSTAmount = IGSTAmount
                purchaseDetail_instance.NetAmount = NetAmount
                purchaseDetail_instance.TAX1Perc = TAX1Perc
                purchaseDetail_instance.TAX1Amount = TAX1Amount
                purchaseDetail_instance.TAX2Perc = TAX2Perc
                purchaseDetail_instance.TAX2Amount = TAX2Amount
                purchaseDetail_instance.TAX3Perc = TAX3Perc
                purchaseDetail_instance.TAX3Amount = TAX3Amount
                purchaseDetail_instance.NetAmount = NetAmount
                purchaseDetail_instance.InclusivePrice = InclusivePrice
                purchaseDetail_instance.BatchCode = BatchCode
                purchaseDetail_instance.LogID = log_instance.ID

                purchaseDetail_instance.save()

            if detailID == 1:
                PurchaseOrderDetailsID = get_auto_id(
                PurchaseOrderDetails, BranchID, CompanyID)
                Action = "A"

                log_instance = PurchaseOrderDetails_Log.objects.create(
                    TransactionID=PurchaseOrderDetailsID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    InclusivePrice=InclusivePrice,
                    BatchCode=BatchCode,
                    CostPerItem=CostPerItem
                )

                PurchaseOrderDetails.objects.create(
                    CompanyID=CompanyID,
                    PurchaseOrderDetailsID=PurchaseOrderDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                    NetAmount=NetAmount,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    InclusivePrice=InclusivePrice,
                    BatchCode=BatchCode,
                    LogID=log_instance.ID,
                    CostPerItem=CostPerItem
                )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders',
                 'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')

    response_data = {
        "StatusCode": 6000,
        "message": "SalesOrder Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseOrderMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        dummyDetails = PurchaseOrderDetailsDummy.objects.filter(
            BranchID=BranchID)

        for dummyDetail in dummyDetails:
            dummyDetail.delete()

        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseOrderMaster.objects.filter(BranchID=BranchID)

            serialized = PurchaseOrderMasterRestSerializer(
                instances, many=True, context={"DataBase": DataBase})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'List',
                         'Purchase Order List Viewed Successfully.', 'Purchase Order List Viewed Successfully')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Purchase Order Master Not Found in this BranchID!"
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
def purchaseOrderMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    CompanyID = data['CompanyID']
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)
        serialized = PurchaseOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID,"PriceRounding": PriceRounding})
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'View',
                     'Purchase Order Single Viewed Successfully.', 'Purchase Order single Viewed Successfully')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseOrderMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    if PurchaseOrderMaster.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk,CompanyID=CompanyID)

        PurchaseOrderMasterID = instance.PurchaseOrderMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        DeliveryDate = instance.DeliveryDate
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
        GrandTotal = instance.GrandTotal
        RoundOff = instance.RoundOff
        IsActive = instance.IsActive
        IsInvoiced = instance.IsInvoiced
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        VATAmount = instance.VATAmount
        SGSTAmount = instance.SGSTAmount
        CGSTAmount = instance.CGSTAmount
        IGSTAmount = instance.IGSTAmount
        TAX1Amount = instance.TAX1Amount
        TAX2Amount = instance.TAX2Amount
        TAX3Amount = instance.TAX3Amount

        Action = "D"

        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            CompanyID=CompanyID,
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
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            IsInvoiced=IsInvoiced,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            TaxID=TaxID,
            TaxType=TaxType,
        )

        instance.delete()

        detail_instances = PurchaseOrderDetails.objects.filter(
            PurchaseOrderMasterID=PurchaseOrderMasterID, BranchID=BranchID)

        for detail_instance in detail_instances:

            PurchaseOrderDetailsID = detail_instance.PurchaseOrderDetailsID
            BranchID = detail_instance.BranchID
            PurchaseOrderMasterID = detail_instance.PurchaseOrderMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            FreeQty = detail_instance.FreeQty
            UnitPrice = detail_instance.UnitPrice
            InclusivePrice = detail_instance.InclusivePrice
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
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount
            NetAmount = detail_instance.NetAmount
            BatchCode = detail_instance.BatchCode
            CostPerItem = detail_instance.CostPerItem

            log_instance = PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                CompanyID=CompanyID,
                BranchID=BranchID,
                Action=Action,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
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
                NetAmount=NetAmount,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                InclusivePrice=InclusivePrice,
                BatchCode=BatchCode,
                CostPerItem=CostPerItem
            )

            detail_instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder',
                     'Delete', 'Purchase Order Deleted Successfully.', 'Purchase Order Deleted Successfully')

        response_data = {
            "StatusCode": 6000,
            "message": "Purchase Order Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseOrder',
                     'Delete', 'Purchase Order Delete failed.', 'Purchase Order Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseOrder_pagination(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']
    filterID = data['filterID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if page_number and items_per_page:
            purchase_object = PurchaseOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            is_data_exist = False
            if filterID == "Pending":
                if purchase_object.filter(IsInvoiced="N").exists():
                    is_data_exist = True
                    purchase_object = purchase_object.filter(IsInvoiced="N")
            elif filterID == "Invoiced":
                if purchase_object.filter(IsInvoiced="I").exists():
                    is_data_exist = True
                    purchase_object = purchase_object.filter(IsInvoiced="I")
            elif filterID == "Cancelled":
                if purchase_object.filter(IsInvoiced="C").exists():
                    is_data_exist = True
                    purchase_object = purchase_object.filter(IsInvoiced="C")
            else:
                is_data_exist = True
                purchase_object = purchase_object

            sale_sort_pagination = list_pagination(
                purchase_object,
                items_per_page,
                page_number
            )
            sale_serializer = PurchaseOrderMasterRestSerializer(
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
                    "count": len(purchase_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def cancel_purchaseOrderMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    today = datetime.datetime.now()

    if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(CompanyID=CompanyID, pk=pk)
        instance.IsInvoiced = "C"
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Purchase Order Cancelled Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Order Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_purchasesOrder(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    PriceRounding = data['PriceRounding']
    FromDate = data['FromDate']
    ToDate = data['ToDate']
    ReportTypes = data['ReportTypes']
    print("---------------------------------------")
    print(ReportTypes)
    print(CompanyID)
    print(BranchID)
    print(FromDate)
    print(ToDate)
    if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,IsInvoiced__in=ReportTypes).exists():
        instance = PurchaseOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,IsInvoiced__in=ReportTypes)

        serialized = PurchaseOrderReportSerializer(instance,many=True, context={"CompanyID": CompanyID,
                                                                          "PriceRounding": PriceRounding, })

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Datas Not Found During this time!"
        }

    return Response(response_data, status=status.HTTP_200_OK)