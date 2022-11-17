from brands.models import POSHoldMaster, POSHoldMaster_Log, POSHoldDetails, POSHoldDetails_Log, POSHoldDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.posholds.serializers import POSHoldMasterSerializer, POSHoldMasterRestSerializer, POSHoldDetailsSerializer, POSHoldDetailsRestSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.posholds.functions import generate_serializer_errors
from rest_framework import status
from api.v1.posholds.functions import get_auto_id, get_auto_idMaster
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_poshold(request):
    today = datetime.datetime.now()

    data = request.data

    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    HoldStatus = data['HoldStatus']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
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
    CreatedUserID = data['CreatedUserID']

    Action = "A"

    POSHoldMasterID = get_auto_idMaster(POSHoldMaster,BranchID)

    POSHoldMaster.objects.create(
        POSHoldMasterID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
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
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
        )

    POSHoldMaster_Log.objects.create(
        TransactionID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
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
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
        )


    posholdDetails = data["POSHoldDetails"]

    for posholdDetail in posholdDetails:

        ProductID = posholdDetail['ProductID']
        Qty = posholdDetail['Qty']
        FreeQty = posholdDetail['FreeQty']
        UnitPrice = posholdDetail['UnitPrice']
        RateWithTax = posholdDetail['RateWithTax']
        CostPerPrice = posholdDetail['CostPerPrice']
        PriceListID = posholdDetail['PriceListID']
        TaxID = posholdDetail['TaxID']
        TaxType = posholdDetail['TaxType']
        DiscountPerc = posholdDetail['DiscountPerc']
        DiscountAmount = posholdDetail['DiscountAmount']
        GrossAmount = posholdDetail['GrossAmount']
        TaxableAmount = posholdDetail['TaxableAmount']
        VATPerc = posholdDetail['VATPerc']
        VATAmount = posholdDetail['VATAmount']
        SGSTPerc = posholdDetail['SGSTPerc']
        SGSTAmount = posholdDetail['SGSTAmount']
        CGSTPerc = posholdDetail['CGSTPerc']
        CGSTAmount = posholdDetail['CGSTAmount']
        IGSTPerc = posholdDetail['IGSTPerc']
        IGSTAmount = posholdDetail['IGSTAmount']
        NetAmount = posholdDetail['NetAmount']
        Flavour = posholdDetail['Flavour']

        
        POSHoldDetailsID = get_auto_id(POSHoldDetails,BranchID)

        
        POSHoldDetails.objects.create(
            POSHoldDetailsID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
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
            Action=Action,
            )

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
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
            Action=Action,
            )

    dummies = POSHoldDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    response_data = {
        "StatusCode" : 6000,
        "message" : "POSHold created Successfully!!!",
        }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_poshold(request,pk):
    today = datetime.datetime.now()

    posholdMaster_instance = None
    posHoldDetails = None

    posholdMaster_instance = POSHoldMaster.objects.get(pk=pk)

    POSHoldMasterID = posholdMaster_instance.POSHoldMasterID
    BranchID = posholdMaster_instance.BranchID
    CreatedUserID = posholdMaster_instance.CreatedUserID

    data = request.data

    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    LedgerID = data['LedgerID']
    PriceCategoryID = data['PriceCategoryID']
    EmployeeID = data['EmployeeID']
    SalesAccount = data['SalesAccount']
    HoldStatus = data['HoldStatus']
    CustomerName = data['CustomerName']
    Address1 = data['Address1']
    Address2 = data['Address2']
    Address3 = data['Address3']
    Notes = data['Notes']
    FinacialYearID = data['FinacialYearID']
    TotalTax = data['TotalTax']
    NetTotal = data['NetTotal']
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

    Action = "M"


    posholdMaster_instance.VoucherNo = VoucherNo
    posholdMaster_instance.InvoiceNo = InvoiceNo
    posholdMaster_instance.Date = Date
    posholdMaster_instance.LedgerID = LedgerID
    posholdMaster_instance.PriceCategoryID = PriceCategoryID
    posholdMaster_instance.EmployeeID = EmployeeID
    posholdMaster_instance.SalesAccount = SalesAccount
    posholdMaster_instance.HoldStatus = HoldStatus
    posholdMaster_instance.CustomerName = CustomerName
    posholdMaster_instance.Address1 = Address1
    posholdMaster_instance.Address2 = Address2
    posholdMaster_instance.Address3 = Address3
    posholdMaster_instance.Notes = Notes
    posholdMaster_instance.FinacialYearID = FinacialYearID
    posholdMaster_instance.TotalTax = TotalTax
    posholdMaster_instance.NetTotal = NetTotal
    posholdMaster_instance.BillDiscount = BillDiscount
    posholdMaster_instance.GrandTotal = GrandTotal
    posholdMaster_instance.RoundOff = RoundOff
    posholdMaster_instance.CashReceived = CashReceived
    posholdMaster_instance.CashAmount = CashAmount
    posholdMaster_instance.BankAmount = BankAmount
    posholdMaster_instance.WarehouseID = WarehouseID
    posholdMaster_instance.TableID = TableID
    posholdMaster_instance.SeatNumber = SeatNumber
    posholdMaster_instance.NoOfGuests = NoOfGuests
    posholdMaster_instance.INOUT = INOUT
    posholdMaster_instance.TokenNumber = TokenNumber
    posholdMaster_instance.IsActive = IsActive
    posholdMaster_instance.Action = Action

    posholdMaster_instance.save()

    POSHoldMaster_Log.objects.create(
        TransactionID=POSHoldMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        LedgerID=LedgerID,
        PriceCategoryID=PriceCategoryID,
        EmployeeID=EmployeeID,
        SalesAccount=SalesAccount,
        HoldStatus=HoldStatus,
        CustomerName=CustomerName,
        Address1=Address1,
        Address2=Address2,
        Address3=Address3,
        Notes=Notes,
        FinacialYearID=FinacialYearID,
        TotalTax=TotalTax,
        NetTotal=NetTotal,
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
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today
        )

    posholdDetails = data["POSHoldDetails"]

    for posholdDetail in posholdDetails:

        pk = posholdDetail["id"]
        ProductID = posholdDetail['ProductID']
        Qty = posholdDetail['Qty']
        FreeQty = posholdDetail['FreeQty']
        UnitPrice = posholdDetail['UnitPrice']
        RateWithTax = posholdDetail['RateWithTax']
        CostPerPrice = posholdDetail['CostPerPrice']
        PriceListID = posholdDetail['PriceListID']
        TaxID = posholdDetail['TaxID']
        TaxType = posholdDetail['TaxType']
        DiscountPerc = posholdDetail['DiscountPerc']
        DiscountAmount = posholdDetail['DiscountAmount']
        GrossAmount = posholdDetail['GrossAmount']
        TaxableAmount = posholdDetail['TaxableAmount']
        VATPerc = posholdDetail['VATPerc']
        VATAmount = posholdDetail['VATAmount']
        SGSTPerc = posholdDetail['SGSTPerc']
        SGSTAmount = posholdDetail['SGSTAmount']
        CGSTPerc = posholdDetail['CGSTPerc']
        CGSTAmount = posholdDetail['CGSTAmount']
        IGSTPerc = posholdDetail['IGSTPerc']
        IGSTAmount = posholdDetail['IGSTAmount']
        NetAmount = posholdDetail['NetAmount']
        Flavour = posholdDetail['Flavour']


        posholdDetails_instance = POSHoldDetails.objects.get(pk=pk)

        POSHoldDetailsID = posholdDetails_instance.POSHoldDetailsID

        posholdDetails_instance.ProductID = ProductID
        posholdDetails_instance.Qty = Qty
        posholdDetails_instance.FreeQty = FreeQty
        posholdDetails_instance.UnitPrice = UnitPrice
        posholdDetails_instance.RateWithTax = RateWithTax
        posholdDetails_instance.CostPerPrice = CostPerPrice
        posholdDetails_instance.PriceListID = PriceListID
        posholdDetails_instance.TaxID = TaxID
        posholdDetails_instance.TaxType = TaxType
        posholdDetails_instance.DiscountPerc = DiscountPerc
        posholdDetails_instance.GrossAmount = GrossAmount
        posholdDetails_instance.TaxableAmount = TaxableAmount
        posholdDetails_instance.VATPerc = VATPerc
        posholdDetails_instance.VATAmount = VATAmount
        posholdDetails_instance.SGSTPerc = SGSTPerc
        posholdDetails_instance.SGSTAmount = SGSTAmount
        posholdDetails_instance.CGSTPerc = CGSTPerc
        posholdDetails_instance.CGSTAmount = CGSTAmount
        posholdDetails_instance.IGSTPerc = IGSTPerc
        posholdDetails_instance.IGSTAmount = IGSTAmount
        posholdDetails_instance.NetAmount = NetAmount
        posholdDetails_instance.Flavour = Flavour
        posholdDetails_instance.Action = Action

        posholdDetails_instance.save()

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
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
            Action=Action,
            )

    response_data = {
        "StatusCode" : 6000,
        "message" : "POSHold Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_posholdMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        dummies = POSHoldDetailsDummy.objects.filter(BranchID=BranchID)

        for dummy in dummies:
            dummy.delete()
        
        if POSHoldMaster.objects.filter(BranchID=BranchID).exists():

            instances = POSHoldMaster.objects.filter(BranchID=BranchID)

            serialized = POSHoldMasterRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "POSHold Master Not Found in this BranchID!"
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
def posholdMaster(request,pk):
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)
    if instance:
        serialized = POSHoldMasterRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_posholdDetails(request,pk):
    instance = None
    if POSHoldDetails.objects.filter(pk=pk).exists():
        instance = POSHoldDetails.objects.get(pk=pk)
    if instance:

        POSHoldDetailsID = instance.POSHoldDetailsID
        BranchID = instance.BranchID
        POSHoldMasterID = instance.POSHoldMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        FreeQty = instance.FreeQty
        UnitPrice = instance.UnitPrice
        RateWithTax = instance.RateWithTax
        CostPerPrice = instance.CostPerPrice
        PriceListID = instance.PriceListID
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        DiscountPerc = instance.DiscountPerc
        DiscountAmount = instance.DiscountAmount
        GrossAmount = instance.GrossAmount
        TaxableAmount = instance.TaxableAmount
        VATPerc = instance.VATPerc
        VATAmount = instance.VATAmount
        SGSTPerc = instance.SGSTPerc
        SGSTAmount = instance.SGSTAmount
        CGSTPerc = instance.CGSTPerc
        CGSTAmount = instance.CGSTAmount
        IGSTPerc = instance.IGSTPerc
        IGSTAmount = instance.IGSTAmount
        NetAmount = instance.NetAmount
        Flavour = instance.Flavour
        Action = "D"

        instance.delete()

        POSHoldDetails_Log.objects.create(
            TransactionID=POSHoldDetailsID,
            BranchID=BranchID,
            POSHoldMasterID=POSHoldMasterID,
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
            Action=Action,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "POSHold Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "POSHold Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_posholdMaster(request,pk):
    today = datetime.datetime.now()
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)
    if instance:

        POSHoldMasterID = instance.POSHoldMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
        HoldStatus = instance.HoldStatus
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
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
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        detail_instances = POSHoldDetails.objects.filter(POSHoldMasterID=POSHoldMasterID)
        
        for detail_instance in detail_instances:

            POSHoldDetailsID = detail_instance.POSHoldDetailsID
            BranchID = detail_instance.BranchID
            POSHoldMasterID = detail_instance.POSHoldMasterID
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

            detail_instance.delete()

            POSHoldDetails_Log.objects.create(
                TransactionID=POSHoldDetailsID,
                BranchID=BranchID,
                POSHoldMasterID=POSHoldMasterID,
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
                Action=Action,
                )

        POSHoldMaster_Log.objects.create(
            TransactionID=POSHoldMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            HoldStatus=HoldStatus,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
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
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "POSHold Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)

