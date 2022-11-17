from brands.models import ReceiptMaster, ReceiptMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.receiptMaster.serializers import ReceiptMasterSerializer, ReceiptMasterRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.receiptMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v3.receiptMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_receiptMaster(request):
    today = datetime.datetime.now()
    serialized = ReceiptMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        SuffixPrefixID = serialized.data['SuffixPrefixID']
        ReceiptNo = serialized.data['ReceiptNo']
        ReferenceNo = serialized.data['ReferenceNo']
        LedgerID = serialized.data['LedgerID']
        EmployeeID = serialized.data['EmployeeID']
        FinancialYearID = serialized.data['FinancialYearID']
        Date = serialized.data['Date']
        TotalAmount = serialized.data['TotalAmount']
        Notes = serialized.data['Notes']
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']

        Action = "A"

        ReceiptMasterID = get_auto_id(ReceiptMaster, BranchID)

        ReceiptMaster.objects.create(
            ReceiptMasterID=ReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            SuffixPrefixID=SuffixPrefixID,
            ReceiptNo=ReceiptNo,
            ReferenceNo=ReferenceNo,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        ReceiptMaster_Log.objects.create(
            TransactionID=ReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            SuffixPrefixID=SuffixPrefixID,
            ReceiptNo=ReceiptNo,
            ReferenceNo=ReferenceNo,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"ReceiptMasterID": ReceiptMasterID}
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
def edit_receiptMaster(request, pk):
    today = datetime.datetime.now()
    serialized = ReceiptMasterSerializer(data=request.data)
    instance = None
    if ReceiptMaster.objects.filter(pk=pk).exists():
        instance = ReceiptMaster.objects.get(pk=pk)

        ReceiptMasterID = instance.ReceiptMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            SuffixPrefixID = serialized.data['SuffixPrefixID']
            ReceiptNo = serialized.data['ReceiptNo']
            ReferenceNo = serialized.data['ReferenceNo']
            LedgerID = serialized.data['LedgerID']
            EmployeeID = serialized.data['EmployeeID']
            FinancialYearID = serialized.data['FinancialYearID']
            Date = serialized.data['Date']
            TotalAmount = serialized.data['TotalAmount']
            Notes = serialized.data['Notes']
            IsActive = serialized.data['IsActive']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.SuffixPrefixID = SuffixPrefixID
            instance.ReceiptNo = ReceiptNo
            instance.ReferenceNo = ReferenceNo
            instance.LedgerID = LedgerID
            instance.EmployeeID = EmployeeID
            instance.FinancialYearID = FinancialYearID
            instance.Date = Date
            instance.TotalAmount = TotalAmount
            instance.Notes = Notes
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            ReceiptMaster_Log.objects.create(
                TransactionID=ReceiptMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                SuffixPrefixID=SuffixPrefixID,
                ReceiptNo=ReceiptNo,
                ReferenceNo=ReferenceNo,
                LedgerID=LedgerID,
                EmployeeID=EmployeeID,
                FinancialYearID=FinancialYearID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"ReceiptMasterID": ReceiptMasterID}
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
            "message": "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_receiptMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if ReceiptMaster.objects.filter(BranchID=BranchID).exists():

            instances = ReceiptMaster.objects.filter(BranchID=BranchID)

            serialized = ReceiptMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt Master not found in this Branch."
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
def receiptMaster(request, pk):
    instance = None
    if ReceiptMaster.objects.filter(pk=pk).exists():
        instance = ReceiptMaster.objects.get(pk=pk)
    if instance:
        serialized = ReceiptMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_receiptMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if ReceiptMaster.objects.filter(pk=pk).exists():
        instance = ReceiptMaster.objects.get(pk=pk)
    if instance:

        ReceiptMasterID = instance.ReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        SuffixPrefixID = instance.SuffixPrefixID
        ReceiptNo = instance.ReceiptNo
        ReferenceNo = instance.ReferenceNo
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        ReceiptMaster_Log.objects.create(
            TransactionID=ReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            SuffixPrefixID=SuffixPrefixID,
            ReceiptNo=ReceiptNo,
            ReferenceNo=ReferenceNo,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Receipt Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
