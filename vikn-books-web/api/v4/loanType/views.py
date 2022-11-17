from brands.models import LoanType, LoanType_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.loanType.serializers import LoanTypeSerializer, LoanTypeRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.loanType.functions import generate_serializer_errors
from rest_framework import status
from api.v4.loanType.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_loanType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoanTypeSerializer(data=request.data)
    print(data['Interest'], "QQQQQQQQQQQQQQQQQQQQ")
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        Name = serialized.data['Name']
        Interest = serialized.data['Interest']

        Action = 'A'
        LoanTypeID = get_auto_id(LoanType, BranchID, CompanyID)
        is_nameExist = False
        NameLow = Name.lower()
        loantypes = LoanType.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for loantype in loantypes:
            name = loantype.Name
            A_Name = name.lower()
            if NameLow == A_Name:
                is_nameExist = True

        print(Name, 'Name')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            LoanType.objects.create(
                LoanTypeID=LoanTypeID,
                BranchID=BranchID,

                Name=Name,
                Interest=Interest,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            LoanType_Log.objects.create(
                BranchID=BranchID,
                LoanTypeID=LoanTypeID,

                Name=Name,
                Interest=Interest,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LoanTypeID": LoanTypeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Period Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_loanType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoanTypeSerializer(data=request.data)
    instance = LoanType.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoanTypeID = instance.LoanTypeID
    instancename = instance.Name
    if serialized.is_valid():
        Name = serialized.data['Name']
        Interest = serialized.data['Interest']

        Action = 'M'
        is_nameExist = False
        Loantype_ok = False

        NameLow = Name.lower()

        Loantypes = LoanType.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for Loantype in Loantypes:
            name = Loantype.Name

            LoantypeName = name.lower()

            if NameLow == LoantypeName:
                is_nameExist = True

            if instancename.lower() == NameLow:

                Loantype_ok = True

        if Loantype_ok:

            instance.Name = Name
            instance.Interest = Interest

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LoanType_Log.objects.create(
                BranchID=BranchID,

                LoanTypeID=LoanTypeID,

                Name=Name,
                Interest=Interest,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LoanTypeID": LoanTypeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Salary Period Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name
                instance.InterestInterest = InterestInterest

                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                LoanType_Log.objects.create(
                    BranchID=BranchID,
                    LoanTypeID=LoanTypeID,

                    Name=Name,
                    Interest=Interest,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"LoanTypeID": LoanTypeID}
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
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def loanTypes(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoanType.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoanType.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LoanTypeRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Period Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def loanType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LoanType.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoanType.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LoanTypeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Period Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_loanType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LoanType.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoanType.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LoanTypeID = instance.LoanTypeID
        Name = instance.Name
        Interest = instance.Interest

        Action = "D"

        instance.delete()

        LoanType_Log.objects.create(
            BranchID=BranchID,

            LoanTypeID=LoanTypeID,
            Name=Name,
            Interest=Interest,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Loan Type Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loan Type Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
