from brands.models import PurchaseMaster, PurchaseMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.purchaseMaster.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.purchaseMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v1.purchaseMaster.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseMaster(request):
    today = datetime.datetime.now()
    serialized = PurchaseMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        RefferenceBillNo = serialized.data['RefferenceBillNo']
        Date = serialized.data['Date']
        VenderInvoiceDate = serialized.data['VenderInvoiceDate']
        CreditPeriod = serialized.data['CreditPeriod']
        LedgerID = serialized.data['LedgerID']
        PriceCategoryID = serialized.data['PriceCategoryID']
        EmployeeID = serialized.data['EmployeeID']
        PurchaseAccount = serialized.data['PurchaseAccount']
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
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']
        
        Action = "A"

        PurchaseMasterID = get_auto_id(PurchaseMaster,BranchID)

        PurchaseMaster.objects.create(
            PurchaseMasterID=PurchaseMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            RefferenceBillNo=RefferenceBillNo,
            Date=Date,
            VenderInvoiceDate=VenderInvoiceDate,
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
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )

        PurchaseMaster_Log.objects.create(
            TransactionID=PurchaseMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            RefferenceBillNo=RefferenceBillNo,
            Date=Date,
            VenderInvoiceDate=VenderInvoiceDate,
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
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )

        data = {"PurchaseMasterID" : PurchaseMasterID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_purchaseMaster(request,pk):
    today = datetime.datetime.now()
    serialized = PurchaseMasterSerializer(data=request.data)
    instance = None
    if PurchaseMaster.objects.filter(pk=pk).exists():
        instance = PurchaseMaster.objects.get(pk=pk)

        PurchaseMasterID = instance.PurchaseMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID
        
    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            RefferenceBillNo = serialized.data['RefferenceBillNo']
            Date = serialized.data['Date']
            VenderInvoiceDate = serialized.data['VenderInvoiceDate']
            CreditPeriod = serialized.data['CreditPeriod']
            LedgerID = serialized.data['LedgerID']
            PriceCategoryID = serialized.data['PriceCategoryID']
            EmployeeID = serialized.data['EmployeeID']
            PurchaseAccount = serialized.data['PurchaseAccount']
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
            IsActive = serialized.data['IsActive']

            Action = "M"


            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.RefferenceBillNo = RefferenceBillNo
            instance.Date = Date
            instance.VenderInvoiceDate = VenderInvoiceDate
            instance.CreditPeriod = CreditPeriod
            instance.LedgerID = LedgerID
            instance.PriceCategoryID = PriceCategoryID
            instance.EmployeeID = EmployeeID
            instance.PurchaseAccount = PurchaseAccount
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
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            PurchaseMaster_Log.objects.create(
                TransactionID=PurchaseMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                RefferenceBillNo=RefferenceBillNo,
                Date=Date,
                VenderInvoiceDate=VenderInvoiceDate,
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
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                )

            data = {"PurchaseMasterID" : PurchaseMasterID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode" : 6001,
                "message" : generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        
        if PurchaseMaster.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseMaster.objects.filter(BranchID=BranchID)

            serialized = PurchaseMasterRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchaseMaster(request,pk):
    instance = None
    if PurchaseMaster.objects.filter(pk=pk).exists():
        instance = PurchaseMaster.objects.get(pk=pk)
    if instance:
        serialized = PurchaseMasterRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseMaster(request,pk):
    today = datetime.datetime.now()
    instance = None
    if PurchaseMaster.objects.filter(pk=pk).exists():
        instance = PurchaseMaster.objects.get(pk=pk)
    if instance:
        PurchaseMasterID = instance.PurchaseMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        RefferenceBillNo = instance.RefferenceBillNo
        Date = instance.Date
        VenderInvoiceDate = instance.VenderInvoiceDate
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
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        PurchaseMaster_Log.objects.create(
            TransactionID=PurchaseMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            RefferenceBillNo=RefferenceBillNo,
            Date=Date,
            VenderInvoiceDate=VenderInvoiceDate,
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
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Purchase Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)