from brands.models import AdvanceRequest, AdvanceRequest_Log, Employee
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.advanceRequest.serializers import AdvanceRequestSerializer, AdvanceRequestRestSerializer, AdvanceApproveSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.advanceRequest.functions import generate_serializer_errors
from rest_framework import status
from api.v8.advanceRequest.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_advanceRequest(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = AdvanceRequestSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        EmployeeId = serialized.data['EmployeeId']
        Amount = serialized.data['Amount']
        NumOfInstalment = serialized.data['NumOfInstalment']
        InstalmentAmount = serialized.data['InstalmentAmount']
        RepaymentDate = serialized.data['RepaymentDate']
        ModeOfPayment = serialized.data['ModeOfPayment']
        PaymentAmount = serialized.data['PaymentAmount']
        PaymentAccount = serialized.data['PaymentAccount']
        print(ModeOfPayment, 'ModeOfPaymentModeOfPayment')

        employee_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)

        Action = 'A'
        AdvanceRequestID = get_auto_id(AdvanceRequest, BranchID, CompanyID)
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
            AdvanceRequest.objects.create(
                AdvanceRequestID=AdvanceRequestID,
                BranchID=BranchID,

                EmployeeId=employee_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Status="Pending",


                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            AdvanceRequest_Log.objects.create(
                BranchID=BranchID,
                AdvanceRequestID=AdvanceRequestID,

                EmployeeId=employee_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"AdvanceRequestID": AdvanceRequestID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Advance Request Name Already Exist!!!"
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
def edit_advanceRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = AdvanceRequestSerializer(data=request.data)
    instance = AdvanceRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    AdvanceRequestID = instance.AdvanceRequestID
    # instancename = instance.Name
    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        Amount = serialized.data['Amount']
        NumOfInstalment = serialized.data['NumOfInstalment']
        InstalmentAmount = serialized.data['InstalmentAmount']
        RepaymentDate = serialized.data['RepaymentDate']
        ModeOfPayment = serialized.data['ModeOfPayment']
        PaymentAmount = serialized.data['PaymentAmount']
        PaymentAccount = serialized.data['PaymentAccount']

        Action = 'M'
        is_nameExist = False
        advanceRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         advanceRequest_ok = True

        if advanceRequest_ok:
            employee_instance = None
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
            if employee_instance:
                instance.EmployeeId = employee_instance
            instance.Amount = Amount
            instance.NumOfInstalment = NumOfInstalment
            instance.InstalmentAmount = InstalmentAmount
            instance.RepaymentDate = RepaymentDate
            instance.ModeOfPayment = ModeOfPayment
            instance.PaymentAmount = PaymentAmount
            instance.PaymentAccount = PaymentAccount

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            AdvanceRequest_Log.objects.create(
                BranchID=BranchID,

                AdvanceRequestID=AdvanceRequestID,

                EmployeeId=employee_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"AdvanceRequestID": AdvanceRequestID}
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
def advanceRequests(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if AdvanceRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = AdvanceRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = AdvanceRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Advance Request Not Found in this BranchID!"
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
def advanceRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if AdvanceRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AdvanceRequest.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = AdvanceRequestRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Advance Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_advanceRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if AdvanceRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AdvanceRequest.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        AdvanceRequestID = instance.AdvanceRequestID

        Action = "D"

        AdvanceRequest_Log.objects.create(
            BranchID=BranchID,

            AdvanceRequestID=AdvanceRequestID,
            EmployeeId=instance.EmployeeId,
            Amount=instance.Amount,
            NumOfInstalment=instance.NumOfInstalment,
            InstalmentAmount=instance.InstalmentAmount,
            RepaymentDate=instance.RepaymentDate,
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
            "message": "Advance Request Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Advance Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def advanceApprovals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if AdvanceRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Status="Pending").exists():
            instances = AdvanceRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Status="Pending")
            serialized = AdvanceRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Advance Request Not Found in this BranchID!"
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
def approve_advanceRequest(request, pk):
    print("::::::::::::::::::::::::HIIII")
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    print(request.data, 'request.data')
    serialized = AdvanceApproveSerializer(data=request.data)
    instance = AdvanceRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    AdvanceRequestID = instance.AdvanceRequestID
    # instancename = instance.Name

    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']

        RepaymentDate = serialized.data['RepaymentDate']
        Amount = serialized.data['Amount']
        NumOfInstalment = serialized.data['NumOfInstalment']
        InstalmentAmount = serialized.data['InstalmentAmount']
        ModeOfPayment = serialized.data['ModeOfPayment']
        PaymentAccount = serialized.data['PaymentAccount']
        PaymentAmount = serialized.data['PaymentAmount']

        # Advance Approve
        # ReasonforApprove = serialized.data['ReasonforApprove']
        Status = serialized.data['Status']

        Action = 'M'
        is_nameExist = False
        AdvanceRequest_ok = True

        if AdvanceRequest_ok:
            employee_instance = None
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
                instance.EmployeeId = employee_instance

            instance.RepaymentDate = RepaymentDate
            instance.Amount = Amount
            instance.NumOfInstalment = NumOfInstalment
            instance.InstalmentAmount = InstalmentAmount
            instance.ModeOfPayment = ModeOfPayment
            instance.PaymentAccount = PaymentAccount
            instance.PaymentAmount = PaymentAmount

            # instance.ReasonforApprove = ReasonforApprove
            instance.Status = Status
            # instance.ApprovedDate = today
            # instance.ApprovedBy = CreatedUserID

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            AdvanceRequest_Log.objects.create(
                BranchID=BranchID,

                AdvanceRequestID=AdvanceRequestID,

                EmployeeId=employee_instance,
                RepaymentDate=RepaymentDate,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                ModeOfPayment=ModeOfPayment,
                PaymentAccount=PaymentAccount,
                PaymentAmount=PaymentAmount,


                Status=Status,
                # ReasonforApprove=ReasonforApprove,
                # ApprovedBy=CreatedUserID,
                # ApprovedDate=today,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"AdvanceRequestID": AdvanceRequestID}
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
