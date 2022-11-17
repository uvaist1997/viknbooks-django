from brands.models import SalesOrderMaster, SalesOrderMaster_Log, SalesOrderDetails, SalesOrderDetails_Log, SalesOrderDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.salesOrders.serializers import SalesOrderMasterSerializer, SalesOrderMasterRestSerializer, SalesOrderDetailsSerializer, SalesOrderDetailsRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.salesOrders.functions import generate_serializer_errors
from rest_framework import status
from api.v2.salesOrders.functions import get_auto_id, get_auto_idMaster
import datetime
from main.functions import get_company, activity_log



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesOrder(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    BranchID = data['BranchID']
    OrderNo = data['OrderNo']
    VoucherNo = data['VoucherNo']
    Date = data['Date']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
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
    CashReceived = data['CashReceived']
    CashAmount = data['CashAmount']
    BankAmount = data['BankAmount']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']
    IsInvoiced = data['IsInvoiced']

    Action = "A"

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = SalesOrderMaster.objects.filter(BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        SalesOrderMasterID = get_auto_idMaster(SalesOrderMaster,BranchID,DataBase)

        SalesOrderMaster.objects.create(
            SalesOrderMasterID=SalesOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsInvoiced=IsInvoiced,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID
            )

        SalesOrderMaster_Log.objects.create(
            TransactionID=SalesOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsInvoiced=IsInvoiced,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID
            )

        saleOrdersDetails = data["saleOrdersDetails"]

        for saleOrdersDetail in saleOrdersDetails:

            # SalesOrderMasterID = serialized.data['SalesOrderMasterID']
            DeliveryDetailsID = saleOrdersDetail['DeliveryDetailsID']
            OrderDetailsID = saleOrdersDetail['OrderDetailsID']
            ProductID = saleOrdersDetail['ProductID']
            Qty = saleOrdersDetail['Qty']
            FreeQty = saleOrdersDetail['FreeQty']
            UnitPrice = saleOrdersDetail['UnitPrice']
            RateWithTax = saleOrdersDetail['RateWithTax']
            CostPerPrice = saleOrdersDetail['CostPerPrice']
            PriceListID = saleOrdersDetail['PriceListID']
            TaxID = saleOrdersDetail['TaxID']
            TaxType = saleOrdersDetail['TaxType']
            DiscountPerc = saleOrdersDetail['DiscountPerc']
            DiscountAmount = saleOrdersDetail['DiscountAmount']
            GrossAmount = saleOrdersDetail['GrossAmount']
            TaxableAmount = saleOrdersDetail['TaxableAmount']
            VATPerc = saleOrdersDetail['VATPerc']
            VATAmount = saleOrdersDetail['VATAmount']
            SGSTPerc = saleOrdersDetail['SGSTPerc']
            SGSTAmount = saleOrdersDetail['SGSTAmount']
            CGSTPerc = saleOrdersDetail['CGSTPerc']
            CGSTAmount = saleOrdersDetail['CGSTAmount']
            IGSTPerc = saleOrdersDetail['IGSTPerc']
            IGSTAmount = saleOrdersDetail['IGSTAmount']
            NetAmount = saleOrdersDetail['NetAmount']
            Flavour = saleOrdersDetail['Flavour']
            
        
            SalesOrderDetailsID = get_auto_id(SalesOrderDetails,BranchID,DataBase)


            SalesOrderDetails.objects.create(
                SalesOrderDetailsID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

            SalesOrderDetails_Log.objects.create(
                TransactionID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'Create', 'Sale Orders created successfully.', 'Sale Orders saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Sale Orders created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sale Orders', 'Create', 'Sale Orders created Failed.', 'VoucherNo already exist!')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_salesOrder(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    salesOrderMaster_instance = None
    salesOrderDetails = None

    salesOrderMaster_instance = SalesOrderMaster.objects.get(pk=pk)

    SalesOrderMasterID = salesOrderMaster_instance.SalesOrderMasterID
    BranchID = salesOrderMaster_instance.BranchID
    VoucherNo = salesOrderMaster_instance.VoucherNo
        
    OrderNo = data['OrderNo']
    Date = data['Date']
    CreditPeriod = data['CreditPeriod']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
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
    CashReceived = data['CashReceived']
    CashAmount = data['CashAmount']
    BankAmount = data['BankAmount']
    WarehouseID = data['WarehouseID']
    TableID = data['TableID']
    SeatNumber = data['SeatNumber']
    NoOfGuests = data['NoOfGuests']
    INOUT = data['INOUT']
    TokenNumber = data['TokenNumber']
    IsActive = data['IsActive']
    IsInvoiced = data['IsInvoiced']

    Action = "M"

    salesOrderMaster_instance.OrderNo = OrderNo
    salesOrderMaster_instance.Date = Date
    salesOrderMaster_instance.CreditPeriod = CreditPeriod
    salesOrderMaster_instance.LedgerID = LedgerID
    salesOrderMaster_instance.PriceCategoryID = PriceCategoryID
    salesOrderMaster_instance.EmployeeID = EmployeeID
    salesOrderMaster_instance.SalesAccount = SalesAccount
    salesOrderMaster_instance.CustomerName = CustomerName
    salesOrderMaster_instance.Address1 = Address1
    salesOrderMaster_instance.Address2 = Address2
    salesOrderMaster_instance.Address3 = Address3
    salesOrderMaster_instance.Notes = Notes
    salesOrderMaster_instance.FinacialYearID = FinacialYearID
    salesOrderMaster_instance.TotalTax = TotalTax
    salesOrderMaster_instance.NetTotal = NetTotal
    salesOrderMaster_instance.AdditionalCost = AdditionalCost
    salesOrderMaster_instance.BillDiscount = BillDiscount
    salesOrderMaster_instance.GrandTotal = GrandTotal
    salesOrderMaster_instance.RoundOff = RoundOff
    salesOrderMaster_instance.CashReceived = CashReceived
    salesOrderMaster_instance.CashAmount = CashAmount
    salesOrderMaster_instance.BankAmount = BankAmount
    salesOrderMaster_instance.WarehouseID = WarehouseID
    salesOrderMaster_instance.TableID = TableID
    salesOrderMaster_instance.SeatNumber = SeatNumber
    salesOrderMaster_instance.NoOfGuests = NoOfGuests
    salesOrderMaster_instance.INOUT = INOUT
    salesOrderMaster_instance.TokenNumber = TokenNumber
    salesOrderMaster_instance.IsActive = IsActive
    salesOrderMaster_instance.IsInvoiced = IsInvoiced
    salesOrderMaster_instance.Action = Action
    salesOrderMaster_instance.UpdatedDate = today
    salesOrderMaster_instance.CreatedUserID = CreatedUserID
    salesOrderMaster_instance.save()

    SalesOrderMaster_Log.objects.create(
        TransactionID=SalesOrderMasterID,
        BranchID=BranchID,
        Action=Action,
        VoucherNo=VoucherNo,
        OrderNo=OrderNo,
        Date=Date,
        CreditPeriod=CreditPeriod,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
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
        CashReceived=CashReceived,
        CashAmount=CashAmount,
        BankAmount=BankAmount,
        WarehouseID=WarehouseID,
        TableID=TableID,
        SeatNumber=SeatNumber,
        NoOfGuests=NoOfGuests,
        INOUT=INOUT,
        TokenNumber=TokenNumber,
        IsActive=IsActive,
        IsInvoiced=IsInvoiced,
        CreatedDate=today,
        UpdatedDate=today,
        CreatedUserID=CreatedUserID
        )

    if SalesOrderDetails.objects.filter(SalesOrderMasterID=SalesOrderMasterID,BranchID=BranchID).exists():

        saleOrdrDetailInstances = SalesOrderDetails.objects.filter(SalesOrderMasterID=SalesOrderMasterID,BranchID=BranchID)

        for saleOrdrDetailInstance in saleOrdrDetailInstances:

            saleOrdrDetailInstances.delete()


    salesOrderDetails = data["saleOrdersDetails"]

    for salesOrderDetail in salesOrderDetails:

        detailID = salesOrderDetail['detailID']
        DeliveryDetailsID = salesOrderDetail['DeliveryDetailsID']
        OrderDetailsID = salesOrderDetail['OrderDetailsID']
        ProductID = salesOrderDetail['ProductID']
        Qty = salesOrderDetail['Qty']
        FreeQty = salesOrderDetail['FreeQty']
        UnitPrice = salesOrderDetail['UnitPrice']
        RateWithTax = salesOrderDetail['RateWithTax']
        CostPerPrice = salesOrderDetail['CostPerPrice']
        PriceListID = salesOrderDetail['PriceListID']
        TaxID = salesOrderDetail['TaxID']
        TaxType = salesOrderDetail['TaxType']
        DiscountPerc = salesOrderDetail['DiscountPerc']
        DiscountAmount = salesOrderDetail['DiscountAmount']
        GrossAmount = salesOrderDetail['GrossAmount']
        TaxableAmount = salesOrderDetail['TaxableAmount']
        VATPerc = salesOrderDetail['VATPerc']
        VATAmount = salesOrderDetail['VATAmount']
        SGSTPerc = salesOrderDetail['SGSTPerc']
        SGSTAmount = salesOrderDetail['SGSTAmount']
        CGSTPerc = salesOrderDetail['CGSTPerc']
        CGSTAmount = salesOrderDetail['CGSTAmount']
        IGSTPerc = salesOrderDetail['IGSTPerc']
        IGSTAmount = salesOrderDetail['IGSTAmount']
        NetAmount = salesOrderDetail['NetAmount']
        Flavour = salesOrderDetail['Flavour']



        SalesOrderDetailsID = get_auto_id(SalesOrderDetails,BranchID,DataBase)

        if detailID == 0:

            SalesOrderDetails.objects.create(
                SalesOrderDetailsID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

            SalesOrderDetails_Log.objects.create(
                TransactionID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

        if detailID == 1:

            Action = "A"

            SalesOrderDetails.objects.create(
                SalesOrderDetailsID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

            SalesOrderDetails_Log.objects.create(
                TransactionID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'Edit', 'Sale Orders Updated successfully.', 'Sale Orders Updated successfully.')

    response_data = {
        "StatusCode" : 6000,
        "message" : "SalesOrder Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_salesOrderMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesOrderMaster.objects.filter(BranchID=BranchID).exists():

            instances = SalesOrderMaster.objects.filter(BranchID=BranchID)

            serialized = SalesOrderMasterRestSerializer(instances,many=True,context = {"DataBase": DataBase })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'List', 'Sale Orders List viewed successfully.', 'Sale Orders List viewed successfully')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Order Master Not Found in this BranchID!"
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
def salesOrderMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(pk=pk)
        serialized = SalesOrderMasterRestSerializer(instance,context = {"DataBase": DataBase })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'View', 'Sale Orders Single viewed successfully.', 'Sale Orders Single viewed successfully')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_salesOrderMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(pk=pk)

        SalesOrderMasterID = instance.SalesOrderMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        OrderNo = instance.OrderNo
        Date = instance.Date
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
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
        CashReceived = instance.CashReceived
        CashAmount = instance.CashAmount
        BankAmount = instance.BankAmount
        WarehouseID = instance.WarehouseID
        TableID = instance.TableID
        SeatNumber = instance.SeatNumber
        NoOfGuests = instance.NoOfGuests
        INOUT = instance.INOUT
        TokenNumber = instance.TokenNumber
        IsActive = instance.IsActive
        IsInvoiced = instance.IsInvoiced

        Action = "D"

        SalesOrderMaster_Log.objects.create(
            TransactionID=SalesOrderMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            OrderNo=OrderNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
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
            CashReceived=CashReceived,
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            IsActive=IsActive,
            IsInvoiced=IsInvoiced,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID
            )

        instance.delete()

        detail_instances = SalesOrderDetails.objects.filter(SalesOrderMasterID=SalesOrderMasterID,BranchID=BranchID)

        for detail_instance in detail_instances:

            SalesOrderDetailsID = detail_instance.SalesOrderDetailsID
            BranchID = detail_instance.BranchID
            SalesOrderMasterID = detail_instance.SalesOrderMasterID
            DeliveryDetailsID = detail_instance.DeliveryDetailsID
            OrderDetailsID = detail_instance.OrderDetailsID
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
            Flavour = detail_instance.Flavour

            SalesOrderDetails_Log.objects.create(
                TransactionID=SalesOrderDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesOrderMasterID=SalesOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrderDetailsID=OrderDetailsID,
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
                NetAmount=NetAmount,
                Flavour=Flavour,
                CreatedDate = today,
                UpdatedDate=today,
                CreatedUserID = CreatedUserID
                )

            detail_instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sale Orders', 'Delete', 'Sale Orders Deleted successfully.', 'Sale Orders Deleted successfully')
     
        response_data = {
            "StatusCode" : 6000,
            "message" : "Sales Order Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)