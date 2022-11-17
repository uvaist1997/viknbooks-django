from brands.models import PaymentMaster, PaymentMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.paymentMaster.serializers import PaymentMasterSerializer, PaymentMasterRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.paymentMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v4.paymentMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_paymentMaster(request):
    today = datetime.datetime.now()
    serialized = PaymentMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = data['BranchID']
        VoucherNo = data['VoucherNo']
        VoucherType = data['VoucherType']
        LedgerID = data['LedgerID']
        EmployeeID = data['EmployeeID']
        PaymentNo = data['PaymentNo']
        FinancialYearID = data['FinancialYearID']
        Date = data['Date']
        TotalAmount = data['TotalAmount']
        Notes = data['Notes']
        IsActive = data['IsActive']
        CreatedUserID = data['CreatedUserID']
        Action = "A"

        PaymentMasterID = get_auto_id(PaymentMaster, BranchID)

        PaymentMaster.objects.create(
            PaymentMasterID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            CreatedUserID=CreatedUserID
        )

        PaymentMaster_Log.objects.create(
            TransactionID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            CreatedUserID=CreatedUserID
        )

        data = {"PaymentMasterID": PaymentMasterID}
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
def edit_paymentMaster(request, pk):
    today = datetime.datetime.now()
    serialized = PaymentMasterSerializer(data=request.data)
    instance = None
    if PaymentMaster.objects.filter(pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)

        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = data['VoucherNo']
            VoucherType = data['VoucherType']
            LedgerID = data['LedgerID']
            EmployeeID = data['EmployeeID']
            PaymentNo = data['PaymentNo']
            FinancialYearID = data['FinancialYearID']
            Date = data['Date']
            TotalAmount = data['TotalAmount']
            Notes = data['Notes']
            IsActive = data['IsActive']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.VoucherType = VoucherType
            instance.LedgerID = LedgerID
            instance.EmployeeID = EmployeeID
            instance.PaymentNo = PaymentNo
            instance.FinancialYearID = FinancialYearID
            instance.Date = Date
            instance.TotalAmount = TotalAmount
            instance.Notes = Notes
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            PaymentMaster_Log.objects.create(
                TransactionID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=LedgerID,
                EmployeeID=EmployeeID,
                PaymentNo=PaymentNo,
                FinancialYearID=FinancialYearID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                IsActive=IsActive,
                CreatedDate=today,
                CreatedUserID=CreatedUserID
            )

            data = {"PaymentMasterID": PaymentMasterID}
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
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_paymentMasters(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if PaymentMaster.objects.filter(BranchID=BranchID).exists():

            instances = PaymentMaster.objects.filter(BranchID=BranchID)

            serialized = PaymentMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Payments"
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
def paymentMaster(request, pk):
    instance = None
    if PaymentMaster.objects.filter(pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)
    if instance:
        serialized = PaymentMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_paymentMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if PaymentMaster.objects.filter(pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)
    if instance:

        PaymentMasterID = instance.PaymentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherType = instance.VoucherType
        LedgerID = instance.LedgerID
        EmployeeID = instance.EmployeeID
        PaymentNo = instance.PaymentNo
        FinancialYearID = instance.FinancialYearID
        Date = instance.Date
        TotalAmount = instance.TotalAmount
        Notes = instance.Notes
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        PaymentMaster_Log.objects.create(
            TransactionID=PaymentMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            VoucherType=VoucherType,
            LedgerID=LedgerID,
            EmployeeID=EmployeeID,
            PaymentNo=PaymentNo,
            FinancialYearID=FinancialYearID,
            Date=Date,
            TotalAmount=TotalAmount,
            Notes=Notes,
            IsActive=IsActive,
            CreatedDate=today,
            CreatedUserID=CreatedUserID
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Payment Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
