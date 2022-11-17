from brands.models import Designation, Designation_Log, Department, Department_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v7.department.serializers import DepartmentSerializer, DepartmentRestSerializer
from api.v7.brands.serializers import ListSerializer
from api.v7.designation.functions import generate_serializer_errors
from rest_framework import status
from api.v7.designation.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime
from rest_framework.permissions import AllowAny, IsAuthenticated


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_department(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DepartmentSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        DepartmentName = serialized.data['DepartmentName']
        ParentDepartment = serialized.data['ParentDepartment']
        ParentDepartment = Department.objects.get(pk=ParentDepartment)
        Notes = serialized.data['Notes']

        Action = 'A'

        DepartmentID = get_auto_DepartmentID(Department, BranchID, CompanyID)
        is_nameExist = False
        DepartmentNameLow = DepartmentName.lower()
        departments = Department.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for department in departments:
            department_name = department.DepartmentName
            departmentName = department_name.lower()
            if DepartmentNameLow == departmentName:
                is_nameExist = True

        if not is_nameExist:
            Department.objects.create(
                DepartmentID=DepartmentID,
                BranchID=BranchID,
                DepartmentName=DepartmentName,
                ParentDepartment=ParentDepartment,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            Department_Log.objects.create(
                TransactionID=DepartmentID,
                BranchID=BranchID,
                DepartmentName=DepartmentName,
                ParentDepartment=ParentDepartment,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Department Name Already Exist!!!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_department(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DepartmentSerializer(data=request.data)
    instance = Department.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    DepartmentID = instance.DepartmentID
    instanceDepartmentName = instance.DepartmentName
    if serialized.is_valid():
        DepartmentName = serialized.data['DepartmentName']
        ParentDepartment = serialized.data['ParentDepartment']
        ParentDepartment = Department.objects.get(pk=ParentDepartment)
        Notes = serialized.data['Notes']
        Action = 'M'
        is_nameExist = False
        department_ok = False

        DepartmentNameLow = DepartmentName.lower()

        departments = Department.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for dep in departments:
            dep_name = dep.DepartmentName

            depName = dep_name.lower()

            if DepartmentNameLow == depName:
                is_nameExist = True

            if instanceDepartmentName.lower() == DepartmentNameLow:

                department_ok = True

        if department_ok:

            instance.DepartmentName = DepartmentName
            instance.ParentDepartment = ParentDepartment
            instance.Notes = Notes
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.Action = Action
            instance.save()

            Department_Log.objects.create(
                TransactionID=DepartmentID,
                BranchID=BranchID,
                DepartmentName=DepartmentName,
                ParentDepartment=ParentDepartment,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Department Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.DepartmentName = DepartmentName
                instance.Notes = Notes
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.Action = Action
                instance.save()

                Department_Log.objects.create(
                    TransactionID=DepartmentID,
                    BranchID=BranchID,
                    DepartmentName=DepartmentName,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def departments(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Department.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Department.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = DepartmentRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Department Not Found in this Branch!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def department(request, pk):
    print("hello")
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Department.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Department.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = DepartmentRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Department Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_department(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Department.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Department.objects.get(pk=pk, CompanyID=CompanyID)
        if not Department.objects.filter(ParentDepartment=instance, CompanyID=CompanyID).exists():
            Action = "D"
            Department_Log.objects.create(
                TransactionID=instance.DepartmentID,
                BranchID=instance.BranchID,
                DepartmentName=instance.DepartmentName,
                Notes=instance.Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            instance.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "Department Deleted Successfully!"
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Department Already exists as parent department!"
            }

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Department Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
