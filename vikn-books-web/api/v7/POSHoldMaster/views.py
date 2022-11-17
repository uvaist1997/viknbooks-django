from brands.models import POSHoldMaster, POSHoldMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v7.POSHoldMaster.serializers import POSHoldMasterSerializer, POSHoldMasterRestSerializer
from api.v7.brands.serializers import ListSerializer
from api.v7.POSHoldMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v7.POSHoldMaster.functions import get_auto_id
import datetime
from rest_framework.permissions import AllowAny, IsAuthenticated


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_posholdMaster(request):
    today = datetime.datetime.now()
    serialized = POSHoldMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        LedgerID = serialized.data['LedgerID']
        PriceCategoryID = serialized.data['PriceCategoryID']
        EmployeeID = serialized.data['EmployeeID']
        SalesAccount = serialized.data['SalesAccount']
        HoldStatus = serialized.data['HoldStatus']
        CustomerName = serialized.data['CustomerName']
        Address1 = serialized.data['Address1']
        Address2 = serialized.data['Address2']
        Address3 = serialized.data['Address3']
        Notes = serialized.data['Notes']
        FinacialYearID = serialized.data['FinacialYearID']
        TotalTax = serialized.data['TotalTax']
        NetTotal = serialized.data['NetTotal']
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
        CreatedUserID = serialized.data['CreatedUserID']
        Action = "A"

        POSHoldMasterID = get_auto_id(POSHoldMaster, BranchID)

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

        data = {"POSHoldMasterID": POSHoldMasterID}
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
def edit_posholdMaster(request, pk):
    today = datetime.datetime.now()
    serialized = POSHoldMasterSerializer(data=request.data)
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)

        POSHoldMasterID = instance.POSHoldMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            LedgerID = serialized.data['LedgerID']
            PriceCategoryID = serialized.data['PriceCategoryID']
            EmployeeID = serialized.data['EmployeeID']
            SalesAccount = serialized.data['SalesAccount']
            HoldStatus = serialized.data['HoldStatus']
            CustomerName = serialized.data['CustomerName']
            Address1 = serialized.data['Address1']
            Address2 = serialized.data['Address2']
            Address3 = serialized.data['Address3']
            Notes = serialized.data['Notes']
            FinacialYearID = serialized.data['FinacialYearID']
            TotalTax = serialized.data['TotalTax']
            NetTotal = serialized.data['NetTotal']
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

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.LedgerID = LedgerID
            instance.PriceCategoryID = PriceCategoryID
            instance.EmployeeID = EmployeeID
            instance.SalesAccount = SalesAccount
            instance.HoldStatus = HoldStatus
            instance.CustomerName = CustomerName
            instance.Address1 = Address1
            instance.Address2 = Address2
            instance.Address3 = Address3
            instance.Notes = Notes
            instance.FinacialYearID = FinacialYearID
            instance.TotalTax = TotalTax
            instance.NetTotal = NetTotal
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
            instance.Action = Action
            instance.save()

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

            data = {"POSHoldMasterID": POSHoldMasterID}
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
            "message": "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_posholdMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if POSHoldMaster.objects.filter(BranchID=BranchID).exists():

            instances = POSHoldMaster.objects.filter(BranchID=BranchID)

            serialized = POSHoldMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "POSHold Master Not Found in this BranchID!"
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
def posholdMaster(request, pk):
    instance = None
    if POSHoldMaster.objects.filter(pk=pk).exists():
        instance = POSHoldMaster.objects.get(pk=pk)
    if instance:
        serialized = POSHoldMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_posholdMaster(request, pk):
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
            "StatusCode": 6000,
            "message": "POSHold Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "POSHold Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
