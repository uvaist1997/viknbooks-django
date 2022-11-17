from brands.models import PurchaseOrderMaster, PurchaseOrderMaster_Log, PurchaseOrderDetails, PurchaseOrderDetails_Log, PurchaseOrderDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.purchaseOrders.serializers import PurchaseOrderMasterSerializer, PurchaseOrderMasterRestSerializer, PurchaseOrderDetailsSerializer, PurchaseOrderDetailsRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.purchaseOrders.functions import generate_serializer_errors
from rest_framework import status
from api.v2.purchaseOrders.functions import get_auto_id, get_auto_idMaster
import datetime
from main.functions import get_company, activity_log



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseOrder(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    BranchID = data['BranchID']
    OrderNo = data['OrderNo']
    Date = data['Date']
    VoucherNo = data['VoucherNo']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    PurchaseAccount = data['PurchaseAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
    AdditionalCost = data['AdditionalCost']
    BillDiscount = data['BillDiscount']
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    IsActive = data['IsActive']

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

    if not is_voucherExist:

        PurchaseOrderMasterID = get_auto_idMaster(PurchaseOrderMaster,BranchID,DataBase)

        PurchaseOrderMaster.objects.create(
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            BillDiscount=BillDiscount,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            )

        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            BillDiscount=BillDiscount,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            )



        purchaseOrderDetails = data["PurchaseOrderDetails"]

        for purchaseOrderDetail in purchaseOrderDetails:

            # PurchaseOrderMasterID = serialized.data['PurchaseOrderMasterID']
            BatchID = purchaseOrderDetail['BatchID']
            DeliveryDetailsID = purchaseOrderDetail['DeliveryDetailsID']
            OrederDetailsID = purchaseOrderDetail['OrederDetailsID']
            ProductID = purchaseOrderDetail['ProductID']
            Qty = purchaseOrderDetail['Qty']
            FreeQty = purchaseOrderDetail['FreeQty']
            UnitPrice = purchaseOrderDetail['UnitPrice']
            RateWithTax = purchaseOrderDetail['RateWithTax']
            CostPerPrice = purchaseOrderDetail['CostPerPrice']
            PriceListID = purchaseOrderDetail['PriceListID']
            TaxID = purchaseOrderDetail['TaxID']
            TaxType = purchaseOrderDetail['TaxType']
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
            
            
            PurchaseOrderDetailsID = get_auto_id(PurchaseOrderDetails,BranchID,DataBase)

            PurchaseOrderDetails.objects.create(
                PurchaseOrderDetailsID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

            PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'Create', 'Purchase Order created successfully.', 'Purchase Order created successfully')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Purchase Order  created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseOrder', 'Create', 'Purchase Order created Failed.', 'VoucherNo already exist!')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_purchaseOrder(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()

    purchaseOrderinstance = None

    purchaseOrderDetails = None
    
    purchaseOrderinstance = PurchaseOrderMaster.objects.get(pk=pk)

    PurchaseOrderMasterID = purchaseOrderinstance.PurchaseOrderMasterID
    BranchID = purchaseOrderinstance.BranchID
    VoucherNo = purchaseOrderinstance.VoucherNo
        
    OrderNo = data['OrderNo']
    Date = data['Date']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    PurchaseAccount = data['PurchaseAccount']
    DeliveryMasterID = data['DeliveryMasterID']
    OrderMasterID = data['OrderMasterID']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
    AdditionalCost = data['AdditionalCost']
    BillDiscount = data['BillDiscount']
    GrandTotal = data['GrandTotal']
    RoundOff = data['RoundOff']
    IsActive = data['IsActive']

    Action = "M"


    purchaseOrderinstance.OrderNo = OrderNo
    purchaseOrderinstance.Date = Date
    purchaseOrderinstance.CreditPeriod = CreditPeriod
    purchaseOrderinstance.LedgerID = LedgerID
    purchaseOrderinstance.PriceCategoryID = PriceCategoryID
    purchaseOrderinstance.EmployeeID = EmployeeID
    purchaseOrderinstance.PurchaseAccount = PurchaseAccount
    purchaseOrderinstance.DeliveryMasterID = DeliveryMasterID
    purchaseOrderinstance.OrderMasterID = OrderMasterID
    purchaseOrderinstance.CustomerName = CustomerName
    purchaseOrderinstance.Address1 = Address1
    purchaseOrderinstance.Address2 = Address2
    purchaseOrderinstance.Address3 = Address3
    purchaseOrderinstance.Notes = Notes
    purchaseOrderinstance.FinacialYearID = FinacialYearID
    purchaseOrderinstance.TotalTax = TotalTax
    purchaseOrderinstance.NetTotal = NetTotal
    purchaseOrderinstance.AdditionalCost = AdditionalCost
    purchaseOrderinstance.BillDiscount = BillDiscount
    purchaseOrderinstance.GrandTotal = GrandTotal
    purchaseOrderinstance.RoundOff = RoundOff
    purchaseOrderinstance.IsActive = IsActive
    purchaseOrderinstance.Action = Action
    purchaseOrderinstance.CreatedUserID = CreatedUserID
    purchaseOrderinstance.UpdatedDate = today

    purchaseOrderinstance.save()

    PurchaseOrderMaster_Log.objects.create(
        TransactionID=PurchaseOrderMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        OrderNo=OrderNo,
        Date=Date,
        CreditPeriod=CreditPeriod,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        PurchaseAccount=PurchaseAccount,
        DeliveryMasterID=DeliveryMasterID,
        OrderMasterID=OrderMasterID,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
        AdditionalCost=AdditionalCost,
        BillDiscount=BillDiscount,
        GrandTotal=GrandTotal,
        RoundOff=RoundOff,
        IsActive=IsActive,
        CreatedDate=today,
        UpdatedDate=today,
        CreatedUserID=CreatedUserID,
        )

    if PurchaseOrderDetails.objects.filter(PurchaseOrderMasterID=PurchaseOrderMasterID,BranchID=BranchID).exists():

        purchaseOrdrDetailInstances = PurchaseOrderDetails.objects.filter(PurchaseOrderMasterID=PurchaseOrderMasterID,BranchID=BranchID)

        for purchaseOrdrDetailInstance in purchaseOrdrDetailInstances:

            purchaseOrdrDetailInstance.delete()

    purchaseOrderDetails = data["PurchaseOrderDetails"]

    for purchaseOrderDetail in purchaseOrderDetails:

        detailID = purchaseOrderDetail['detailID']
        DeliveryDetailsID = purchaseOrderDetail['DeliveryDetailsID']
        OrederDetailsID = purchaseOrderDetail['OrederDetailsID']
        ProductID = purchaseOrderDetail['ProductID']
        Qty = purchaseOrderDetail['Qty']
        FreeQty = purchaseOrderDetail['FreeQty']
        UnitPrice = purchaseOrderDetail['UnitPrice']
        RateWithTax = purchaseOrderDetail['RateWithTax']
        CostPerPrice = purchaseOrderDetail['CostPerPrice']
        PriceListID = purchaseOrderDetail['PriceListID']
        TaxID = purchaseOrderDetail['TaxID']
        TaxType = purchaseOrderDetail['TaxType']
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
        BatchID = purchaseOrderDetail['BatchID']

        PurchaseOrderDetailsID = get_auto_id(PurchaseOrderDetails,BranchID,DataBase)

        if detailID == 0:

            PurchaseOrderDetails.objects.create(
                PurchaseOrderDetailsID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

            PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )
        
        if detailID == 1:

            Action = "A"

            PurchaseOrderDetails.objects.create(
                PurchaseOrderDetailsID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

            PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'Edit', 'Purchase Order updated Successfully.', 'Purchase Order updated Successfully')

    response_data = {
    "StatusCode" : 6000,
    "message" : "Purchase Order Updated Successfully!!!",
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

        dummyDetails = PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID)

        for dummyDetail in dummyDetails:
            dummyDetail.delete()
        
        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseOrderMaster.objects.filter(BranchID=BranchID)

            serialized = PurchaseOrderMasterRestSerializer(instances,many=True,context = {"DataBase": DataBase })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'List', 'Purchase Order List Viewed Successfully.', 'Purchase Order List Viewed Successfully')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Master Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchaseOrderMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)
    if instance:
        serialized = PurchaseOrderMasterRestSerializer(instance,context = {"DataBase": DataBase })
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'View', 'Purchase Order Single Viewed Successfully.', 'Purchase Order single Viewed Successfully')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseOrderMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)
    if instance:

        PurchaseOrderMasterID = instance.PurchaseOrderMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        OrderNo = instance.OrderNo
        Date = instance.Date
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        PurchaseAccount = instance.PurchaseAccount
        DeliveryMasterID = instance.DeliveryMasterID
        OrderMasterID = instance.OrderMasterID
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
        AdditionalCost = instance.AdditionalCost
        BillDiscount = instance.BillDiscount
        GrandTotal = instance.GrandTotal
        RoundOff = instance.RoundOff
        IsActive = instance.IsActive

        Action = "D"

        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AdditionalCost=AdditionalCost,
            BillDiscount=BillDiscount,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        instance.delete()

        detail_instances = PurchaseOrderDetails.objects.filter(PurchaseOrderMasterID=PurchaseOrderMasterID,BranchID=BranchID)

        for detail_instance in detail_instances:

            PurchaseOrderDetailsID = detail_instance.PurchaseOrderDetailsID
            BranchID = detail_instance.BranchID
            PurchaseOrderMasterID = detail_instance.PurchaseOrderMasterID
            DeliveryDetailsID = detail_instance.DeliveryDetailsID
            OrederDetailsID = detail_instance.OrederDetailsID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            FreeQty = detail_instance.FreeQty
            UnitPrice = detail_instance.UnitPrice
            RateWithTax = detail_instance.RateWithTax
            CostPerPrice = detail_instance.CostPerPrice
            PriceListID = detail_instance.PriceListID
            TaxID = detail_instance.TaxID
            TaxType = detail_instance.TaxType
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
            BatchID = detail_instance.BatchID


            PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                BatchID=BatchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
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
                NetAmount = NetAmount
                )

            detail_instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseOrder', 'Delete', 'Purchase Order Deleted Successfully.', 'Purchase Order Deleted Successfully')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Purchase Order Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseOrder', 'Delete', 'Purchase Order Delete failed.', 'Purchase Order Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)