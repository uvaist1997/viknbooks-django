from brands.models import JournalMaster, JournalMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.journalMaster.serializers import JournalMasterSerializer, JournalMasterRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.journalMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v10.journalMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_journalMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = JournalMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        Notes = serialized.data['Notes']
        TotalDebit = serialized.data['TotalDebit']
        TotalCredit = serialized.data['TotalCredit']
        Difference = serialized.data['Difference']
        IsActive = serialized.data['IsActive']

        Action = "A"

        JournalMasterID = get_auto_id(JournalMaster, BranchID, DataBase)

        JournalMaster.objects.create(
            JournalMasterID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            Difference=Difference,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
        )

        JournalMaster_Log.objects.create(
            TransactionID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            Difference=Difference,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
        )

        data = {"JournalMasterID": JournalMasterID}
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_journalMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = JournalMasterSerializer(data=request.data)
    instance = None
    if JournalMaster.objects.filter(pk=pk).exists():
        instance = JournalMaster.objects.get(pk=pk)

        JournalMasterID = instance.JournalMasterID
        BranchID = instance.BranchID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            Notes = serialized.data['Notes']
            TotalDebit = serialized.data['TotalDebit']
            TotalCredit = serialized.data['TotalCredit']
            Difference = serialized.data['Difference']
            IsActive = serialized.data['IsActive']
            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.Notes = Notes
            instance.TotalDebit = TotalDebit
            instance.TotalCredit = TotalCredit
            instance.Difference = Difference
            instance.IsActive = IsActive
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            JournalMaster_Log.objects.create(
                TransactionID=JournalMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                Date=Date,
                Notes=Notes,
                TotalDebit=TotalDebit,
                TotalCredit=TotalCredit,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"JournalMasterID": JournalMasterID}
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
            "message": "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def journalMasters(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if JournalMaster.objects.filter(BranchID=BranchID).exists():

            instances = JournalMaster.objects.filter(BranchID=BranchID)

            serialized = JournalMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Journal Master not found in this branch."
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def journalMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if JournalMaster.objects.filter(pk=pk).exists():
        instance = JournalMaster.objects.get(pk=pk)
    if instance:
        serialized = JournalMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_journalMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if JournalMaster.objects.filter(pk=pk).exists():
        instance = JournalMaster.objects.get(pk=pk)
        JournalMasterID = instance.JournalMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        Notes = instance.Notes
        TotalDebit = instance.TotalDebit
        TotalCredit = instance.TotalCredit
        IsActive = instance.IsActive
        Action = "D"
        instance.delete()

        JournalMaster_Log.objects.create(
            TransactionID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Journal Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
