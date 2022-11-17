from brands.models import SalaryComponent, SalaryComponent_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.salaryComponent.serializers import SalaryComponentSerializer, SalaryComponentRestSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.salaryComponent.functions import generate_serializer_errors
from rest_framework import status
from api.v8.salaryComponent.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_salaryComponent(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryComponentSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        Name = serialized.data['Name']
        Description = serialized.data['Description']
        ComponentType = serialized.data['ComponentType']
        ExpressionType = serialized.data['ExpressionType']
        ExpressionValue = serialized.data['ExpressionValue']
        Status = serialized.data['Status']

        Action = 'A'
        SalaryComponentID = get_auto_id(SalaryComponent, BranchID, CompanyID)
        is_nameExist = False
        NameLow = Name.lower()
        salarycomponents = SalaryComponent.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for salarycomponents in salarycomponents:
            name = salarycomponents.Name
            A_Name = name.lower()
            if NameLow == A_Name:
                is_nameExist = True

        print(Name, 'Name')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            SalaryComponent.objects.create(
                SalaryComponentID=SalaryComponentID,
                BranchID=BranchID,

                Name=Name,
                Description=Description,
                ComponentType=ComponentType,
                ExpressionType=ExpressionType,
                ExpressionValue=ExpressionValue,
                Status=Status,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            SalaryComponent_Log.objects.create(
                BranchID=BranchID,
                SalaryComponentID=SalaryComponentID,

                Name=Name,
                Description=Description,
                ComponentType=ComponentType,
                ExpressionType=ExpressionType,
                ExpressionValue=ExpressionValue,
                Status=Status,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"SalaryComponentID": SalaryComponentID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "SalaryComponent Name Already Exist!!!"
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
def edit_salaryComponent(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryComponentSerializer(data=request.data)
    instance = SalaryComponent.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    SalaryComponentID = instance.SalaryComponentID
    instancename = instance.Name
    if serialized.is_valid():
        Name = serialized.data['Name']
        Description = serialized.data['Description']
        ComponentType = serialized.data['ComponentType']
        ExpressionType = serialized.data['ExpressionType']
        ExpressionValue = serialized.data['ExpressionValue']
        Status = serialized.data['Status']

        Action = 'M'
        is_nameExist = False
        salarycomponent_ok = False

        NameLow = Name.lower()

        salarycomponents = SalaryComponent.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for salarycomponent in salarycomponents:
            name = salarycomponent.Name

            salarycomponentName = name.lower()

            if NameLow == salarycomponentName:
                is_nameExist = True

            if instancename.lower() == NameLow:

                salarycomponent_ok = True

        if salarycomponent_ok:

            instance.Name = Name
            instance.Description = Description
            instance.ComponentType = ComponentType
            instance.ExpressionType = ExpressionType
            instance.ExpressionValue = ExpressionValue
            instance.Status = Status

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            SalaryComponent_Log.objects.create(
                BranchID=BranchID,

                SalaryComponentID=SalaryComponentID,

                Name=Name,
                Description=Description,
                ComponentType=ComponentType,
                ExpressionType=ExpressionType,
                ExpressionValue=ExpressionValue,
                Status=Status,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"SalaryComponentID": SalaryComponentID}
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
                    "message": "SalaryComponent Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name
                instance.Description = Description
                instance.ComponentType = ComponentType
                instance.ExpressionType = ExpressionType
                instance.ExpressionValue = ExpressionValue
                instance.Status = Status
                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                SalaryComponent_Log.objects.create(
                    BranchID=BranchID,
                    SalaryComponentID=SalaryComponentID,

                    Name=Name,
                    Description=Description,
                    ComponentType=ComponentType,
                    ExpressionType=ExpressionType,
                    ExpressionValue=ExpressionValue,
                    Status=Status,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"SalaryComponentID": SalaryComponentID}
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
def salaryComponents(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalaryComponent.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = SalaryComponent.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = SalaryComponentRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Component Not Found in this BranchID!"
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
def salaryComponent(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if SalaryComponent.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryComponent.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = SalaryComponentRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Component Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_salaryComponent(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalaryComponent.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryComponent.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        SalaryComponentID = instance.SalaryComponentID
        Name = instance.Name
        Description = instance.Description
        ComponentType = instance.ComponentType
        ExpressionType = instance.ExpressionType
        ExpressionValue = instance.ExpressionValue
        Status = instance.Status

        Action = "D"

        instance.delete()

        SalaryComponent_Log.objects.create(
            BranchID=BranchID,

            SalaryComponentID=SalaryComponentID,
            Name=Name,
            Description=Description,
            ComponentType=ComponentType,
            ExpressionType=ExpressionType,
            ExpressionValue=ExpressionValue,
            Status=Status,

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "SalaryComponent Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "SalaryComponent Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
