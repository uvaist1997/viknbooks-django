from brands.models import SalesOrderMaster, SalesOrderMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.salesOrderMaster.serializers import SalesOrderMasterSerializer, SalesOrderMasterRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.salesOrderMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v3.salesOrderMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesOrderMaster(request):
    today = datetime.datetime.now()
    serialized = SalesOrderMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        OrderNo = serialized.data['OrderNo']
        Date = serialized.data['Date']
        CreditPeriod = serialized.data['CreditPeriod']
        LedgerID = serialized.data['LedgerID']
        PriceCategoryID = serialized.data['PriceCategoryID']
        EmployeeID = serialized.data['EmployeeID']
        SalesAccount = serialized.data['SalesAccount']
        CustomerName = serialized.data['CustomerName']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        Notes = serialized.data['Notes']
        OldTransactionID = serialized.data['OldTransactionID']
        FinacialYearID = serialized.data['FinacialYearID']
        TotalTax = serialized.data['TotalTax']
        NetTotal = serialized.data['NetTotal']
        AdditionalCost = serialized.data['AdditionalCost']
        BillDiscount = serialized.data['BillDiscount']
        GrandTotal = serialized.data['GrandTotal']
        RoundOff = serialized.data['RoundOff']
        CashReceived = serialized.data['CashReceived']
        CashAmount = serialized.data['CashAmount']
        BankAmount = serialized.data['BankAmount']
        WarehouseID = serialized.data['WarehouseID']
        TableID = serialized.data['TableID']
        SeatNumber = serialized.data['SeatNumber']
        NoOfGuests = serialized.data['NoOfGuests']
        INOUT = serialized.data['INOUT']
        TokenNumber = serialized.data['TokenNumber']
        IsActive = serialized.data['IsActive']
        IsInvoiced = serialized.data['IsInvoiced']
        CreatedUserID = serialized.data['CreatedUserID']

        Action = "A"

        SalesOrderMasterID = get_auto_id(SalesOrderMaster, BranchID)

        SalesOrderMaster.objects.create(
            SalesOrderMasterID=SalesOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            OldTransactionID=OldTransactionID,
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
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        SalesOrderMaster_Log.objects.create(
            TransactionID=SalesOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            OldTransactionID=OldTransactionID,
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
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"SalesOrderMasterID": SalesOrderMasterID}
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
def edit_salesOrderMaster(request, pk):
    today = datetime.datetime.now()
    serialized = SalesOrderMasterSerializer(data=request.data)
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(pk=pk)

        SalesOrderMasterID = instance.SalesOrderMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            OrderNo = serialized.data['OrderNo']
            Date = serialized.data['Date']
            CreditPeriod = serialized.data['CreditPeriod']
            LedgerID = serialized.data['LedgerID']
            PriceCategoryID = serialized.data['PriceCategoryID']
            EmployeeID = serialized.data['EmployeeID']
            SalesAccount = serialized.data['SalesAccount']
            CustomerName = serialized.data['CustomerName']
            Address1 = serialized.data['Address1']
            Address2 = serialized.data['Address2']
            Address3 = serialized.data['Address3']
            Notes = serialized.data['Notes']
            OldTransactionID = serialized.data['OldTransactionID']
            FinacialYearID = serialized.data['FinacialYearID']
            TotalTax = serialized.data['TotalTax']
            NetTotal = serialized.data['NetTotal']
            AdditionalCost = serialized.data['AdditionalCost']
            BillDiscount = serialized.data['BillDiscount']
            GrandTotal = serialized.data['GrandTotal']
            RoundOff = serialized.data['RoundOff']
            CashReceived = serialized.data['CashReceived']
            CashAmount = serialized.data['CashAmount']
            BankAmount = serialized.data['BankAmount']
            WarehouseID = serialized.data['WarehouseID']
            TableID = serialized.data['TableID']
            SeatNumber = serialized.data['SeatNumber']
            NoOfGuests = serialized.data['NoOfGuests']
            INOUT = serialized.data['INOUT']
            TokenNumber = serialized.data['TokenNumber']
            IsActive = serialized.data['IsActive']
            IsInvoiced = serialized.data['IsInvoiced']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.OrderNo = OrderNo
            instance.Date = Date
            instance.CreditPeriod = CreditPeriod
            instance.LedgerID = LedgerID
            instance.PriceCategoryID = PriceCategoryID
            instance.EmployeeID = EmployeeID
            instance.SalesAccount = SalesAccount
            instance.CustomerName = CustomerName
            instance.Address1 = Address1
            instance.Address2 = Address2
            instance.Address3 = Address3
            instance.Notes = Notes
            instance.OldTransactionID = OldTransactionID
            instance.FinacialYearID = FinacialYearID
            instance.TotalTax = TotalTax
            instance.NetTotal = NetTotal
            instance.AdditionalCost = AdditionalCost
            instance.BillDiscount = BillDiscount
            instance.GrandTotal = GrandTotal
            instance.RoundOff = RoundOff
            instance.CashReceived = CashReceived
            instance.CashAmount = CashAmount
            instance.BankAmount = BankAmount
            instance.WarehouseID = WarehouseID
            instance.TableID = TableID
            instance.SeatNumber = SeatNumber
            instance.NoOfGuests = NoOfGuests
            instance.INOUT = INOUT
            instance.TokenNumber = TokenNumber
            instance.IsActive = IsActive
            instance.IsInvoiced = IsInvoiced
            instance.Action = Action
            instance.save()

            SalesOrderMaster_Log.objects.create(
                TransactionID=SalesOrderMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
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
                OldTransactionID=OldTransactionID,
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
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"SalesOrderMasterID": SalesOrderMasterID}
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
            "message": "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_salesOrderMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesOrderMaster.objects.filter(BranchID=BranchID).exists():

            instances = SalesOrderMaster.objects.filter(BranchID=BranchID)

            serialized = SalesOrderMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Order Master Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesOrderMaster(request, pk):
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(pk=pk)
    if instance:
        serialized = SalesOrderMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_salesOrderMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if SalesOrderMaster.objects.filter(pk=pk).exists():
        instance = SalesOrderMaster.objects.get(pk=pk)
    if instance:

        SalesOrderMasterID = instance.SalesOrderMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
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
        OldTransactionID = instance.OldTransactionID
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
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        SalesOrderMaster_Log.objects.create(
            TransactionID=SalesOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            OldTransactionID=OldTransactionID,
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
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Sales Order Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
