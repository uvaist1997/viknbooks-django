from brands.models import JournalDetails, JournalDetails_Log, JournalDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.journalDetails.serializers import JournalDetailsSerializer, JournalDetailsRestSerializer, JournalDetailsDummySerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.journalDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v9.journalDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_journalDetail(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = JournalDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        JournalMasterID = serialized.data['JournalMasterID']
        LedgerID = serialized.data['LedgerID']
        Debit = serialized.data['Debit']
        Credit = serialized.data['Credit']
        Narration = serialized.data['Narration']

        Action = "A"

        JournalDetailsID = get_auto_id(JournalDetails, BranchID, DataBase)

        JournalDetails.objects.create(
            JournalDetailsID=JournalDetailsID,
            BranchID=BranchID,
            JournalMasterID=JournalMasterID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        JournalDetails_Log.objects.create(
            TransactionID=JournalDetailsID,
            BranchID=BranchID,
            JournalMasterID=JournalMasterID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )

        data = {"JournalDetailsID": JournalDetailsID}
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
def edit_journalDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = JournalDetailsSerializer(data=request.data)
    instance = None
    if JournalDetails.objects.filter(pk=pk).exists():
        instance = JournalDetails.objects.get(pk=pk)

        JournalDetailsID = instance.JournalDetailsID
        BranchID = instance.BranchID
        JournalMasterID = instance.JournalMasterID

        if serialized.is_valid():
            LedgerID = serialized.data['LedgerID']
            Debit = serialized.data['Debit']
            Credit = serialized.data['Credit']
            Narration = serialized.data['Narration']

            Action = "M"

            instance.LedgerID = LedgerID
            instance.Debit = Debit
            instance.Credit = Credit
            instance.Narration = Narration
            instance.UpdatedDate = today
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.save()

            JournalDetails_Log.objects.create(
                TransactionID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
            )

            data = {"JournalDetailsID": JournalDetailsID}
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
            "message": "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def journalDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if JournalDetails.objects.filter(BranchID=BranchID).exists():

            instances = JournalDetails.objects.filter(BranchID=BranchID)

            serialized = JournalDetailsRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Journal Details Not Found in this BranchID!"
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
def journalDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if JournalDetails.objects.filter(pk=pk).exists():
        instance = JournalDetails.objects.get(pk=pk)
        serialized = JournalDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journalDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if JournalDetails.objects.filter(pk=pk).exists():
        instance = JournalDetails.objects.get(pk=pk)
    if instance:
        JournalDetailsID = instance.JournalDetailsID
        BranchID = instance.BranchID
        JournalMasterID = instance.JournalMasterID
        LedgerID = instance.LedgerID
        Debit = instance.Debit
        Credit = instance.Credit
        Narration = instance.Narration
        Action = "D"

        instance.delete()

        JournalDetails_Log.objects.create(
            TransactionID=JournalDetailsID,
            BranchID=BranchID,
            JournalMasterID=JournalMasterID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Journal Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_journalDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    JournalDetailsID = data['JournalDetailsID']
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    Debit = data['Debit']
    Credit = data['Credit']
    Narration = data['Narration']

    detailID = 0

    JournalDetailsDummy.objects.create(
        JournalDetailsID=JournalDetailsID,
        BranchID=BranchID,
        LedgerID=LedgerID,
        Debit=Debit,
        Credit=Credit,
        Narration=Narration,
        detailID=detailID
    )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditJournalMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = JournalDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        JournalDetailsID = dummydetail['JournalDetailsID']
        BranchID = dummydetail['BranchID']
        LedgerID = dummydetail['LedgerID']
        Debit = dummydetail['Debit']
        Credit = dummydetail['Credit']
        Narration = dummydetail['Narration']
        detailID = 0

        JournalDetailsDummy.objects.create(
            JournalDetailsID=JournalDetailsID,
            BranchID=BranchID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            detailID=detailID
        )
    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_journalDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if JournalDetailsDummy.objects.filter(BranchID=BranchID).exists():

            debit = 0
            credit = 0

            instances = JournalDetailsDummy.objects.filter(BranchID=BranchID)

            for instance in instances:

                debit += instance.Debit
                credit += int(instance.Credit)

            serialized = JournalDetailsDummySerializer(
                instances, many=True, context={"DataBase": DataBase})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "TotalDebit": debit,
                "TotalCredit": credit,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "BranchID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_journalDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if JournalDetailsDummy.objects.filter(pk=pk).exists():

        instance = JournalDetailsDummy.objects.get(pk=pk)

        data = request.data

        JournalDetailsID = data['JournalDetailsID']
        BranchID = data['BranchID']
        LedgerID = data['LedgerID']
        Debit = data['Debit']
        Credit = data['Credit']
        Narration = data['Narration']
        detailID = data['detailID']

        instance.JournalDetailsID = JournalDetailsID
        instance.BranchID = BranchID
        instance.LedgerID = LedgerID
        instance.Debit = Debit
        instance.Credit = Credit
        instance.Narration = Narration
        instance.detailID = detailID
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Successfully updated!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journalDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if JournalDetailsDummy.objects.filter(pk=pk).exists():
        instance = JournalDetailsDummy.objects.get(pk=pk)
    if instance:

        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Product Removed Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
