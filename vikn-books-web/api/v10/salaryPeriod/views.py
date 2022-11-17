from brands.models import SalaryPeriod, SalaryPeriod_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.salaryPeriod.serializers import SalaryPeriodSerializer, SalaryPeriodRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.salaryPeriod.functions import generate_serializer_errors
from rest_framework import status
from api.v10.salaryPeriod.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_salaryPeriod(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryPeriodSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        Name = serialized.data['Name']
        Note = serialized.data['Note']
        Year = serialized.data['Year']

        try:
            FromDate = request.data['FromDate']
            FromDate_str = str(FromDate) + ' 08:15:27.243860'
            FromDate = datetime.datetime.strptime(
                FromDate_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            FromDate = None

        try:
            ToDate = request.data['ToDate']
            ToDate_str = str(ToDate) + ' 08:15:27.243860'
            ToDate = datetime.datetime.strptime(
                ToDate_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            ToDate = None

        Action = 'A'
        SalaryPeriodID = get_auto_id(SalaryPeriod, BranchID, CompanyID)
        is_nameExist = False
        NameLow = Name.lower()
        salaryperiods = SalaryPeriod.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for salaryperiod in salaryperiods:
            name = salaryperiod.Name
            A_Name = name.lower()
            if NameLow == A_Name:
                is_nameExist = True

        print(Name, 'Name')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            SalaryPeriod.objects.create(
                SalaryPeriodID=SalaryPeriodID,
                BranchID=BranchID,

                Name=Name,
                Note=Note,
                Year=Year,
                FromDate=FromDate,
                ToDate=ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            SalaryPeriod_Log.objects.create(
                BranchID=BranchID,
                SalaryPeriodID=SalaryPeriodID,

                Name=Name,
                Note=Note,
                Year=Year,
                FromDate=FromDate,
                ToDate=ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"SalaryPeriodID": SalaryPeriodID}
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_salaryPeriod(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryPeriodSerializer(data=request.data)
    instance = SalaryPeriod.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    SalaryPeriodID = instance.SalaryPeriodID
    instancename = instance.Name
    if serialized.is_valid():
        Name = serialized.data['Name']
        Note = serialized.data['Note']
        Year = serialized.data['Year']
        # FromDate = serialized.data['FromDate']
        # ToDate = serialized.data['ToDate']

        Action = 'M'
        is_nameExist = False
        salaryperiod_ok = False

        NameLow = Name.lower()

        salaryperiods = SalaryPeriod.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for salaryperiod in salaryperiods:
            name = salaryperiod.Name

            salaryperiodName = name.lower()

            if NameLow == salaryperiodName:
                is_nameExist = True

            if instancename.lower() == NameLow:

                salaryperiod_ok = True

        if salaryperiod_ok:

            instance.Name = Name
            instance.Note = Note
            instance.Year = Year

            try:
                FromDate = request.data['FromDate']
                FromDate_str = str(FromDate) + ' 08:15:27.243860'
                FromDate = datetime.datetime.strptime(
                    FromDate_str, '%Y-%m-%d %H:%M:%S.%f')
                print(FromDate, "try")
            except:
                print("except")
                FromDate = instance.FromDate

            try:
                ToDate = request.data['ToDate']
                ToDate_str = str(ToDate) + ' 08:15:27.243860'
                ToDate = datetime.datetime.strptime(
                    ToDate_str, '%Y-%m-%d %H:%M:%S.%f')
            except:
                ToDate = instance.ToDate

            instance.ToDate = ToDate
            instance.FromDate = FromDate
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            SalaryPeriod_Log.objects.create(
                BranchID=BranchID,

                SalaryPeriodID=SalaryPeriodID,

                Name=Name,
                Note=Note,
                Year=Year,
                FromDate=FromDate,
                ToDate=ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"SalaryPeriodID": SalaryPeriodID}
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
                instance.Note = Note
                instance.Year = Year
                instance.FromDate = FromDate
                instance.ToDate = ToDate

                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                SalaryPeriod_Log.objects.create(
                    BranchID=BranchID,
                    SalaryPeriodID=SalaryPeriodID,

                    Name=Name,
                    Note=Note,
                    Year=Year,
                    FromDate=FromDate,
                    ToDate=ToDate,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"SalaryPeriodID": SalaryPeriodID}
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salaryPeriods(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalaryPeriod.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = SalaryPeriod.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = SalaryPeriodRestSerializer(instances, many=True)
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salaryPeriod(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if SalaryPeriod.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryPeriod.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = SalaryPeriodRestSerializer(instance)
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_salaryPeriod(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalaryPeriod.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryPeriod.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        SalaryPeriodID = instance.SalaryPeriodID
        Name = instance.Name
        Note = instance.Note
        Year = instance.Year
        FromDate = instance.FromDate
        ToDate = instance.ToDate

        Action = "D"

        instance.delete()

        SalaryPeriod_Log.objects.create(
            BranchID=BranchID,

            SalaryPeriodID=SalaryPeriodID,
            Name=Name,
            Note=Note,
            Year=Year,
            FromDate=FromDate,
            ToDate=ToDate,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Salary Period Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Period Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
