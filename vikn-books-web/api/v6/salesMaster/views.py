from brands.models import SalesMaster, SalesMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.salesMaster.serializers import SalesMasterSerializer, SalesMasterRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.salesMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v6.salesMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesMaster(request):
    today = datetime.datetime.now()
    serialized = SalesMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        CreditPeriod = serialized.data['CreditPeriod']
        LedgerID = serialized.data['LedgerID']
        PriceCategoryID = serialized.data['PriceCategoryID']
        EmployeeID = serialized.data['EmployeeID']
        SalesAccount = serialized.data['SalesAccount']
        DeliveryMasterID = serialized.data['DeliveryMasterID']
        OrderMasterID = serialized.data['OrderMasterID']
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
        CashAmount = serialized.data['CashAmount']
        BankAmount = serialized.data['BankAmount']
        WarehouseID = serialized.data['WarehouseID']
        TableID = serialized.data['TableID']
        SeatNumber = serialized.data['SeatNumber']
        NoOfGuests = serialized.data['NoOfGuests']
        INOUT = serialized.data['INOUT']
        TokenNumber = serialized.data['TokenNumber']
        CardTypeID = serialized.data['CardTypeID']
        CardNumber = serialized.data['CardNumber']
        IsActive = serialized.data['IsActive']
        IsPosted = serialized.data['IsPosted']
        SalesType = serialized.data['SalesType']
        CreatedUserID = serialized.data['CreatedUserID']

        Action = "A"

        SalesMasterID = get_auto_id(SalesMaster, BranchID)

        SalesMaster.objects.create(
            SalesMasterID=SalesMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
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
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            CardTypeID=CardTypeID,
            CardNumber=CardNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        SalesMaster_Log.objects.create(
            TransactionID=SalesMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
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
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            CardTypeID=CardTypeID,
            CardNumber=CardNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"SalesMasterID": SalesMasterID}
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
def edit_salesMaster(request, pk):
    today = datetime.datetime.now()
    serialized = SalesMasterSerializer(data=request.data)
    instance = None
    if SalesMaster.objects.filter(pk=pk).exists():
        instance = SalesMaster.objects.get(pk=pk)

        SalesMasterID = instance.SalesMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            CreditPeriod = serialized.data['CreditPeriod']
            LedgerID = serialized.data['LedgerID']
            PriceCategoryID = serialized.data['PriceCategoryID']
            EmployeeID = serialized.data['EmployeeID']
            SalesAccount = serialized.data['SalesAccount']
            DeliveryMasterID = serialized.data['DeliveryMasterID']
            OrderMasterID = serialized.data['OrderMasterID']
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
            CashAmount = serialized.data['CashAmount']
            BankAmount = serialized.data['BankAmount']
            WarehouseID = serialized.data['WarehouseID']
            TableID = serialized.data['TableID']
            SeatNumber = serialized.data['SeatNumber']
            NoOfGuests = serialized.data['NoOfGuests']
            INOUT = serialized.data['INOUT']
            TokenNumber = serialized.data['TokenNumber']
            CardTypeID = serialized.data['CardTypeID']
            CardNumber = serialized.data['CardNumber']
            IsActive = serialized.data['IsActive']
            IsPosted = serialized.data['IsPosted']
            SalesType = serialized.data['SalesType']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.CreditPeriod = CreditPeriod
            instance.LedgerID = LedgerID
            instance.PriceCategoryID = PriceCategoryID
            instance.EmployeeID = EmployeeID
            instance.SalesAccount = SalesAccount
            instance.DeliveryMasterID = DeliveryMasterID
            instance.OrderMasterID = OrderMasterID
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
            instance.CashAmount = CashAmount
            instance.BankAmount = BankAmount
            instance.WarehouseID = WarehouseID
            instance.TableID = TableID
            instance.SeatNumber = SeatNumber
            instance.NoOfGuests = NoOfGuests
            instance.INOUT = INOUT
            instance.TokenNumber = TokenNumber
            instance.CardTypeID = CardTypeID
            instance.CardNumber = CardNumber
            instance.IsActive = IsActive
            instance.IsPosted = IsPosted
            instance.SalesType = SalesType
            instance.Action = Action
            instance.save()

            SalesMaster_Log.objects.create(
                TransactionID=SalesMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                Date=Date,
                CreditPeriod=CreditPeriod,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                EmployeeID=EmployeeID,
                SalesAccount=SalesAccount,
                DeliveryMasterID=DeliveryMasterID,
                OrderMasterID=OrderMasterID,
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
                CashAmount=CashAmount,
                BankAmount=BankAmount,
                WarehouseID=WarehouseID,
                TableID=TableID,
                SeatNumber=SeatNumber,
                NoOfGuests=NoOfGuests,
                INOUT=INOUT,
                TokenNumber=TokenNumber,
                CardTypeID=CardTypeID,
                CardNumber=CardNumber,
                IsActive=IsActive,
                IsPosted=IsPosted,
                SalesType=SalesType,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"SalesMasterID": SalesMasterID}
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
            "message": "Sales Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_salesMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesMaster.objects.filter(BranchID=BranchID).exists():

            instances = SalesMaster.objects.filter(BranchID=BranchID)

            serialized = SalesMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def salesMaster(request, pk):
    instance = None
    if SalesMaster.objects.filter(pk=pk).exists():
        instance = SalesMaster.objects.get(pk=pk)
    if instance:
        serialized = SalesMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_salesMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if SalesMaster.objects.filter(pk=pk).exists():
        instance = SalesMaster.objects.get(pk=pk)
    if instance:
        SalesMasterID = instance.SalesMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
        DeliveryMasterID = instance.DeliveryMasterID
        OrderMasterID = instance.OrderMasterID
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
        CashAmount = instance.CashAmount
        BankAmount = instance.BankAmount
        WarehouseID = instance.WarehouseID
        TableID = instance.TableID
        SeatNumber = instance.SeatNumber
        NoOfGuests = instance.NoOfGuests
        INOUT = instance.INOUT
        TokenNumber = instance.TokenNumber
        CardTypeID = instance.CardTypeID
        CardNumber = instance.CardNumber
        IsActive = instance.IsActive
        IsPosted = instance.IsPosted
        SalesType = instance.SalesType
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        # point_instances  = LoyaltyPoint.objects.filter(LoyaltyCustomerID__id=loyalty_instance.pk,BranchID=BranchID, CompanyID=CompanyID,is_Radeem=False)
        SalesMaster_Log.objects.create(
            TransactionID=SalesMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            DeliveryMasterID=DeliveryMasterID,
            OrderMasterID=OrderMasterID,
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
            CashAmount=CashAmount,
            BankAmount=BankAmount,
            WarehouseID=WarehouseID,
            TableID=TableID,
            SeatNumber=SeatNumber,
            NoOfGuests=NoOfGuests,
            INOUT=INOUT,
            TokenNumber=TokenNumber,
            CardTypeID=CardTypeID,
            CardNumber=CardNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "Sales Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
