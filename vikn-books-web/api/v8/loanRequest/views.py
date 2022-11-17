from brands.models import LoanRequest, LoanRequest_Log, Employee, LoanType
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.loanRequest.serializers import LoanRequestSerializer, LoanRequestRestSerializer, LoanApproveSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.loanRequest.functions import generate_serializer_errors
from rest_framework import status
from api.v8.loanRequest.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_loanRequest(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoanRequestSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        EmployeeId = serialized.data['EmployeeId']
        LoanTypeID = serialized.data['LoanTypeID']
        Amount = serialized.data['Amount']
        NumOfInstalment = serialized.data['NumOfInstalment']
        InstalmentAmount = serialized.data['InstalmentAmount']
        RepaymentDate = serialized.data['RepaymentDate']
        ModeOfPayment = serialized.data['ModeOfPayment']
        PaymentAmount = serialized.data['PaymentAmount']
        PaymentAccount = serialized.data['PaymentAccount']
        Interest = serialized.data['Interest']

        print(ModeOfPayment, 'ModeOfPaymentModeOfPayment')

        employee_instance = None
        loantype_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)
        if LoanType.objects.filter(pk=LoanTypeID).exists():
            loantype_instance = LoanType.objects.get(pk=LoanTypeID)

        Action = 'A'
        LoanRequestID = get_auto_id(LoanRequest, BranchID, CompanyID)
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
            LoanRequest.objects.create(
                LoanRequestID=LoanRequestID,
                BranchID=BranchID,

                EmployeeId=employee_instance,
                LoanTypeID=loantype_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Interest=Interest,
                Status="Pending",


                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            LoanRequest_Log.objects.create(
                BranchID=BranchID,
                LoanRequestID=LoanRequestID,
                LoanTypeID=loantype_instance,

                EmployeeId=employee_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Interest=Interest,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LoanRequestID": LoanRequestID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loan Request Name Already Exist!!!"
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
def edit_loanRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LoanRequestSerializer(data=request.data)
    instance = LoanRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoanRequestID = instance.LoanRequestID
    # instancename = instance.Name
    if serialized.is_valid():
        EmployeeId = serialized.data['EmployeeId']
        LoanTypeID = serialized.data['LoanTypeID']
        Amount = serialized.data['Amount']
        NumOfInstalment = serialized.data['NumOfInstalment']
        InstalmentAmount = serialized.data['InstalmentAmount']
        RepaymentDate = serialized.data['RepaymentDate']
        ModeOfPayment = serialized.data['ModeOfPayment']
        PaymentAmount = serialized.data['PaymentAmount']
        Interest = serialized.data['Interest']
        PaymentAccount = serialized.data['PaymentAccount']

        Action = 'M'
        is_nameExist = False
        loanRequest_ok = True

        # NameLow = Name.lower()

        # salaryperiods = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salaryperiod in salaryperiods:
        #     name = salaryperiod.Name

        #     salaryperiodName = name.lower()

        #     if NameLow == salaryperiodName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         LoanRequest_ok = True

        if loanRequest_ok:
            employee_instance = None
            loantype_instance = None
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
            if LoanType.objects.filter(pk=LoanTypeID).exists():
                loantype_instance = LoanType.objects.get(pk=LoanTypeID)

            if employee_instance:
                instance.EmployeeId = employee_instance
            if loantype_instance:
                instance.LoanTypeID = loantype_instance
            instance.Amount = Amount
            instance.NumOfInstalment = NumOfInstalment
            instance.InstalmentAmount = InstalmentAmount
            instance.RepaymentDate = RepaymentDate
            instance.ModeOfPayment = ModeOfPayment
            instance.PaymentAmount = PaymentAmount
            instance.PaymentAccount = PaymentAccount
            instance.Interest = Interest

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LoanRequest_Log.objects.create(
                BranchID=BranchID,

                LoanRequestID=LoanRequestID,

                EmployeeId=employee_instance,
                LoanTypeID=loantype_instance,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                RepaymentDate=RepaymentDate,
                ModeOfPayment=ModeOfPayment,
                PaymentAmount=PaymentAmount,
                PaymentAccount=PaymentAccount,
                Interest=Interest,
                Status="Pending",

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LoanRequestID": LoanRequestID}
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
def loanRequests(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoanRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LoanRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LoanRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loan Request Not Found in this BranchID!"
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
def loanRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LoanRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoanRequest.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LoanRequestRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loan Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_loanRequest(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LoanRequest.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LoanRequest.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LoanRequestID = instance.LoanRequestID

        Action = "D"

        LoanRequest_Log.objects.create(
            BranchID=BranchID,

            LoanRequestID=LoanRequestID,
            EmployeeId=instance.EmployeeId,
            LoanTypeID=instance.LoanTypeID,
            Amount=instance.Amount,
            NumOfInstalment=instance.NumOfInstalment,
            InstalmentAmount=instance.InstalmentAmount,
            RepaymentDate=instance.RepaymentDate,
            Interest=instance.Interest,
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
            "message": "Loan Request Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Loan Request Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def loanApprovals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LoanRequest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Status="Pending").exists():
            instances = LoanRequest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, Status="Pending")
            serialized = LoanRequestRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Loan Request Not Found in this BranchID!"
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
def approve_loanRequest(request, pk):
    print("::::::::::::::::::::::::HIIII")
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    print(request.data, 'request.data')
    serialized = LoanApproveSerializer(data=request.data)
    instance = LoanRequest.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LoanRequestID = instance.LoanRequestID
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
        Interest = serialized.data['Interest']

        # Loan Approve
        # ReasonforApprove = serialized.data['ReasonforApprove']
        Status = serialized.data['Status']

        Action = 'M'
        is_nameExist = False
        LoanRequest_ok = True

        if LoanRequest_ok:
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
            instance.Interest = Interest

            # instance.ReasonforApprove = ReasonforApprove
            instance.Status = Status
            # instance.ApprovedDate = today
            # instance.ApprovedBy = CreatedUserID

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LoanRequest_Log.objects.create(
                BranchID=BranchID,

                LoanRequestID=LoanRequestID,

                EmployeeId=employee_instance,
                RepaymentDate=RepaymentDate,
                Amount=Amount,
                NumOfInstalment=NumOfInstalment,
                InstalmentAmount=InstalmentAmount,
                ModeOfPayment=ModeOfPayment,
                PaymentAccount=PaymentAccount,
                PaymentAmount=PaymentAmount,
                Interest=Interest,


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

            data = {"LoanRequestID": LoanRequestID}
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
