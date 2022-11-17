from brands.models import RelieveRequest, RelieveRequest_Log, Employee
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.relieveRequest.serializers import RelieveRequestSerializer, RelieveRequestRestSerializer, RelieveApproveSerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.relieveRequest.functions import generate_serializer_errors
from rest_framework import status
from api.v5.relieveRequest.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_relieveRequest(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = RelieveRequestSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        EmployeeId = serialized.data['EmployeeId']
        RequestDate = serialized.data['RequestDate']
        Reportto = serialized.data['Reportto']
        ReliveType = serialized.data['ReliveType']
        ReasonforRelive = serialized.data['ReasonforRelive']

        employee_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)

        Action = 'A'
        RelieveRequestID = get_auto_id(RelieveRequest, BranchID, CompanyID)
        is_nameExist = False
        # NameLow = Name.lower()
        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)
        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name
        #     A_Name = name.lower()
        #     if NameLow == A_Name:
        #         is_nameExist = True

        # print(Name,'Name')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            RelieveRequest.objects.create(
                RelieveRequestID=RelieveRequestID,
                BranchID=BranchID,

                EmployeeId=employee_instance,
                RequestDate=RequestDate,
                Reportto=Reportto,
                ReliveType=ReliveType,
                ReasonforRelive=ReasonforRelive,

                Status="Pending",


                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            RelieveRequest_Log.objects.create(
                BranchID=BranchID,
                RelieveRequestID=RelieveRequestID,

                EmployeeId=employee_instance,
                RequestDate=RequestDate,
                Reportto=Reportto,
                ReliveType=ReliveType,
                ReasonforRelive=ReasonforRelive,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"RelieveRequestID": RelieveRequestID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Relieve Request Name Already Exist!!!"
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
def edit_relieveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = RelieveRequestSerializer(data=request.data)
    instance = RelieveRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    RelieveRequestID = instance.RelieveRequestID
    # instancename = instance.Name
    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        RequestDate = serialized.data['RequestDate']
        Reportto = serialized.data['Reportto']
        ReliveType = serialized.data['ReliveType']
        ReasonforRelive = serialized.data['ReasonforRelive']

        Action = 'M'
        is_nameExist = False
        RelieveRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         RelieveRequest_ok = True

        if RelieveRequest_ok:
            employee_instance = None
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
            if employee_instance:
                instance.EmployeeId = employee_instance
            instance.RequestDate = RequestDate
            instance.Reportto = Reportto
            instance.ReliveType = ReliveType
            instance.ReasonforRelive = ReasonforRelive

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            RelieveRequest_Log.objects.create(
                BranchID=BranchID,

                RelieveRequestID=RelieveRequestID,

                EmployeeId=employee_instance,
                RequestDate=RequestDate,
                Reportto=Reportto,
                ReliveType=ReliveType,
                ReasonforRelive=ReasonforRelive,

                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"RelieveRequestID": RelieveRequestID}
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
def relieveRequests(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if RelieveRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = RelieveRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = RelieveRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Relieve Request Not Found in this BranchID!"
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
def relieveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if RelieveRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = RelieveRequest.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = RelieveRequestRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Relieve Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_relieveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if RelieveRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = RelieveRequest.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        RelieveRequestID = instance.RelieveRequestID

        Action = "D"

        RelieveRequest_Log.objects.create(
            BranchID=BranchID,

            RelieveRequestID=RelieveRequestID,
            EmployeeId=instance.EmployeeId,
            RequestDate=instance.RequestDate,
            Reportto=instance.Reportto,
            ReliveType=instance.ReliveType,
            ReasonforRelive=instance.ReasonforRelive,
            Status=instance.Status,

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )
        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Relieve Request Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Relieve Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def relieveApprovals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if RelieveRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Status="Pending").exists():
            instances = RelieveRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Status="Pending")
            serialized = RelieveRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Relieve Request Not Found in this BranchID!"
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
def approve_relieveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    print(request.data, 'request.data')
    serialized = RelieveApproveSerializer(data=request.data)
    instance = RelieveRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    RelieveRequestID = instance.RelieveRequestID
    # instancename = instance.Name

    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        RequestDate = serialized.data['RequestDate']
        Reportto = serialized.data['Reportto']
        ReliveType = serialized.data['ReliveType']
        ReasonforRelive = serialized.data['ReasonforRelive']

        # Relieve Approve
        ReasonforApprove = serialized.data['ReasonforApprove']
        Status = serialized.data['Status']

        print(ReasonforApprove, Status, 'Status',
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        Action = 'M'
        is_nameExist = False
        RelieveRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         RelieveRequest_ok = True

        if RelieveRequest_ok:
            employee_instance = None
            # Relievetype_instance = None
            # if RelieveType.objects.filter(pk=RelieveTypeID).exists():
            #     Relievetype_instance = RelieveType.objects.get(pk=RelieveTypeID)
            #     instance.RelieveTypeID = Relievetype_instance
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
                instance.EmployeeId = employee_instance
            instance.RequestDate = RequestDate
            instance.Reportto = Reportto
            instance.ReliveType = ReliveType
            instance.ReasonforRelive = ReasonforRelive

            instance.ReasonforApprove = ReasonforApprove
            instance.Status = Status
            instance.ApprovedDate = today
            instance.ApprovedBy = CreatedUserID

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            RelieveRequest_Log.objects.create(
                BranchID=BranchID,

                RelieveRequestID=RelieveRequestID,

                EmployeeId=employee_instance,
                RequestDate=RequestDate,
                Reportto=Reportto,
                ReliveType=ReliveType,
                ReasonforRelive=ReasonforRelive,

                Status=Status,
                ReasonforApprove=ReasonforApprove,
                ApprovedBy=CreatedUserID,
                ApprovedDate=today,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"RelieveRequestID": RelieveRequestID}
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
