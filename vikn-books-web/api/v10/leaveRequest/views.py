from brands.models import LeaveRequest, LeaveRequest_Log, Employee, LeaveType
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.leaveRequest.serializers import LeaveRequestSerializer, LeaveRequestRestSerializer, LeaveApproveSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.leaveRequest.functions import generate_serializer_errors
from rest_framework import status
from api.v10.leaveRequest.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_leaveRequest(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveRequestSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        EmployeeId = serialized.data['EmployeeId']
        FromDate = serialized.data['FromDate']
        ToDate = serialized.data['ToDate']
        Reportto = serialized.data['Reportto']
        LeaveTypeID = serialized.data['LeaveTypeID']
        ReasonforLeave = serialized.data['ReasonforLeave']

        leavetype_instance = None
        if LeaveType.objects.filter(pk=LeaveTypeID).exists():
            leavetype_instance = LeaveType.objects.get(pk=LeaveTypeID)
        employee_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)

        Action = 'A'
        LeaveRequestID = get_auto_id(LeaveRequest, BranchID, CompanyID)
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
            LeaveRequest.objects.create(
                LeaveRequestID=LeaveRequestID,
                BranchID=BranchID,

                EmployeeId=employee_instance,
                FromDate=FromDate,
                ToDate=ToDate,
                Reportto=Reportto,
                LeaveTypeID=leavetype_instance,
                ReasonforLeave=ReasonforLeave,

                Status="Pending",


                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            LeaveRequest_Log.objects.create(
                BranchID=BranchID,
                LeaveRequestID=LeaveRequestID,


                EmployeeId=employee_instance,
                FromDate=FromDate,
                ToDate=ToDate,
                Reportto=Reportto,
                LeaveTypeID=leavetype_instance,
                ReasonforLeave=ReasonforLeave,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LeaveRequestID": LeaveRequestID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Leave Request Name Already Exist!!!"
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
def edit_leaveRequest(request, pk):
    data = request.data
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveRequestSerializer(data=request.data)
    instance = LeaveRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LeaveRequestID = instance.LeaveRequestID
    # instancename = instance.Name

    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        FromDate = serialized.data['FromDate']
        ToDate = serialized.data['ToDate']
        Reportto = serialized.data['Reportto']
        LeaveTypeID = serialized.data['LeaveTypeID']
        ReasonforLeave = serialized.data['ReasonforLeave']

        Action = 'M'
        is_nameExist = False
        LeaveRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         LeaveRequest_ok = True

        if LeaveRequest_ok:
            employee_instance = None
            leavetype_instance = None
            if LeaveType.objects.filter(pk=LeaveTypeID).exists():
                leavetype_instance = LeaveType.objects.get(pk=LeaveTypeID)
                instance.LeaveTypeID = leavetype_instance
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
                instance.EmployeeId = employee_instance
            instance.FromDate = FromDate
            instance.ToDate = ToDate
            instance.Reportto = Reportto
            # instance.LeaveTypeID = LeaveType
            instance.ReasonforLeave = ReasonforLeave

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LeaveRequest_Log.objects.create(
                BranchID=BranchID,

                LeaveRequestID=LeaveRequestID,

                EmployeeId=employee_instance,
                FromDate=FromDate,
                ToDate=ToDate,
                Reportto=Reportto,
                LeaveTypeID=leavetype_instance,
                ReasonforLeave=ReasonforLeave,

                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LeaveRequestID": LeaveRequestID}
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
def leaveRequests(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LeaveRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LeaveRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LeaveRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Leave Request Not Found in this BranchID!"
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
def leaveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LeaveRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LeaveRequest.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LeaveRequestRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Leave Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_leaveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LeaveRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LeaveRequest.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LeaveRequestID = instance.LeaveRequestID

        Action = "D"

        LeaveRequest_Log.objects.create(
            BranchID=BranchID,


            LeaveRequestID=LeaveRequestID,
            EmployeeId=instance.EmployeeId,
            FromDate=instance.FromDate,
            ToDate=instance.ToDate,
            Reportto=instance.Reportto,
            LeaveTypeID=instance.LeaveTypeID,
            ReasonforLeave=instance.ReasonforLeave,
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
            "message": "Leave Request Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Leave Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def leaveApprovals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LeaveRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Status="Pending").exists():
            instances = LeaveRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Status="Pending")
            serialized = LeaveRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Leave Request Not Found in this BranchID!"
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
def approve_leaveRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    print(request.data, 'request.data')
    serialized = LeaveApproveSerializer(data=request.data)
    instance = LeaveRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LeaveRequestID = instance.LeaveRequestID
    # instancename = instance.Name

    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        FromDate = serialized.data['FromDate']
        ToDate = serialized.data['ToDate']
        Reportto = serialized.data['Reportto']
        LeaveTypeID = serialized.data['LeaveTypeID']
        ReasonforLeave = serialized.data['ReasonforLeave']

        # Leave Approve
        ReasonforApprove = serialized.data['ReasonforApprove']
        Status = serialized.data['Status']

        print(ReasonforApprove, Status, 'Status',
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        Action = 'M'
        is_nameExist = False
        LeaveRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         LeaveRequest_ok = True

        if LeaveRequest_ok:
            employee_instance = None
            leavetype_instance = None
            if LeaveType.objects.filter(pk=LeaveTypeID).exists():
                leavetype_instance = LeaveType.objects.get(pk=LeaveTypeID)
                instance.LeaveTypeID = leavetype_instance
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
                instance.EmployeeId = employee_instance
            instance.FromDate = FromDate
            instance.ToDate = ToDate
            instance.Reportto = Reportto
            # instance.LeaveTypeID = LeaveType
            instance.ReasonforLeave = ReasonforLeave

            instance.ReasonforApprove = ReasonforApprove
            instance.Status = Status
            instance.ApprovedDate = today
            instance.ApprovedBy = CreatedUserID

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LeaveRequest_Log.objects.create(
                BranchID=BranchID,

                LeaveRequestID=LeaveRequestID,

                EmployeeId=employee_instance,
                FromDate=FromDate,
                ToDate=ToDate,
                Reportto=Reportto,
                LeaveTypeID=leavetype_instance,
                ReasonforLeave=ReasonforLeave,

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

            data = {"LeaveRequestID": LeaveRequestID}
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
