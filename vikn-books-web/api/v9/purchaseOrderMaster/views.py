from brands.models import PurchaseOrderMaster, PurchaseOrderMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.purchaseOrderMaster.serializers import PurchaseOrderMasterSerializer, PurchaseOrderMasterRestSerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.purchaseOrderMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v9.purchaseOrderMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseOrderMaster(request):
    today = datetime.datetime.now()
    serialized = PurchaseOrderMasterSerializer(data=request.data)
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
        BillDiscPercent = serialized.data['BillDiscPercent']
        BillDiscAmt = serialized.data['BillDiscAmt']
        print(BillDiscPercent,BillDiscAmt,'ZAAZAZAZAZAAZAZAAZAZAAZAZA^^^^^^^^^^^^^^^^^')

        Action = "A"

         # ===================================
        try:
            ShippingCharge = data['ShippingCharge']
        except:
            ShippingCharge = 0

        try:
            shipping_tax_amount = data['shipping_tax_amount']
        except:
            shipping_tax_amount = 0

        try:
            TaxTypeID = data['TaxTypeID']
        except:
            TaxTypeID = ""

        try:
            SAC = data['SAC']
        except:
            SAC = ""

        try:
            PurchaseTax = data['PurchaseTax']
        except:
            PurchaseTax = 0

            # ===================================

        PurchaseOrderMasterID = get_auto_id(PurchaseOrderMaster, BranchID)

        PurchaseOrderMaster.objects.create(
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            BillDiscAmt=BillDiscAmt,
            CompanyID=CompanyID,
            ShippingCharge=ShippingCharge,
            shipping_tax_amount=shipping_tax_amount,
            TaxTypeID=TaxTypeID,
            SAC=SAC,
            PurchaseTax=PurchaseTax,
        )

        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            BillDiscAmt=BillDiscAmt,
            CompanyID=CompanyID,
            ShippingCharge=ShippingCharge,
            shipping_tax_amount=shipping_tax_amount,
            TaxTypeID=TaxTypeID,
            SAC=SAC,
            PurchaseTax=PurchaseTax,
        )

        data = {"PurchaseOrderMasterID": PurchaseOrderMasterID}
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
def edit_purchaseOrderMaster(request, pk):
    today = datetime.datetime.now()
    serialized = PurchaseOrderMasterSerializer(data=request.data)
    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)

        PurchaseOrderMasterID = instance.PurchaseOrderMasterID
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
            BillDiscPercent = serialized.data['BillDiscPercent']
            BillDiscAmt = serialized.data['BillDiscAmt']

            Action = "M"

             # ================
            try:
                ShippingCharge = data['ShippingCharge']
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data['shipping_tax_amount']
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data['TaxTypeID']
            except:
                TaxTypeID = ""

            try:
                SAC = data['SAC']
            except:
                SAC = ""

            try:
                PurchaseTax = data['PurchaseTax']
            except:
                PurchaseTax = 0
            # ==========

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.OrderNo = OrderNo
            instance.Date = Date
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
            instance.BillDiscPercent = BillDiscPercent
            instance.BillDiscAmt = BillDiscAmt
            purchaseMaster_instance.ShippingCharge = ShippingCharge
            purchaseMaster_instance.shipping_tax_amount = shipping_tax_amount
            purchaseMaster_instance.TaxTypeID = TaxTypeID
            purchaseMaster_instance.SAC = SAC
            purchaseMaster_instance.PurchaseTax = PurchaseTax
            instance.save()

            PurchaseOrderMaster_Log.objects.create(
                TransactionID=PurchaseOrderMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
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
                BillDiscAmt=BillDiscAmt,
                CompanyID=CompanyID,
                ShippingCharge=ShippingCharge,
                shipping_tax_amount=shipping_tax_amount,
                TaxTypeID=TaxTypeID,
                SAC=SAC,
                PurchaseTax=PurchaseTax,
            )

            data = {"PurchaseOrderMasterID": PurchaseOrderMasterID}
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
            "message": "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseOrderMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if PurchaseOrderMaster.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseOrderMaster.objects.filter(BranchID=BranchID)

            serialized = PurchaseOrderMasterRestSerializer(
                instances, many=True)

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


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchaseOrderMaster(request, pk):
    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)
    if instance:
        serialized = PurchaseOrderMasterRestSerializer(instance)
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
    today = datetime.datetime.now()
    instance = None
    if PurchaseOrderMaster.objects.filter(pk=pk).exists():
        instance = PurchaseOrderMaster.objects.get(pk=pk)
    if instance:

        PurchaseOrderMasterID = instance.PurchaseOrderMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
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
        PurchaseOrderMaster_Log.objects.create(
            TransactionID=PurchaseOrderMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
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
            "StatusCode": 6000,
            "message": "Purchase Order Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Order Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
