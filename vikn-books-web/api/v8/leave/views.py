from brands.models import Leave, Leave_Log, Employee, Category, LeaveType, LeaveDetails, LeaveDetails_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.leave.serializers import LeaveSerializer, LeaveRestSerializer, LeaveSingleSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.leave.functions import generate_serializer_errors
from rest_framework import status
from api.v8.leave.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_leave(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        FinancialYear = serialized.data['FinancialYear']
        PreviousYear = serialized.data['PreviousYear']
        Type = serialized.data['Type']
        DepartmentID = serialized.data['DepartmentID']
        DesignationID = serialized.data['DesignationID']
        EmployeeId = serialized.data['EmployeeId']
        EmployeeCode = serialized.data['EmployeeCode']
        CategoryId = serialized.data['CategoryId']
        Balance = serialized.data['Balance']

        CategoryId = None
        EmployeeId = None
        if Type == "Category":
            CategoryId = serialized.data['CategoryId']
        else:
            EmployeeId = serialized.data['EmployeeId']

        print(CategoryId, "CategoryId")

        LeaveDetails_list = data['LeaveDetails']

        try:
            EmployeeCode = serialized.data['EmployeeCode']
        except:
            EmployeeCode = 0

        Action = 'A'
        LeaveID = get_auto_id(Leave, BranchID, CompanyID)
        is_nameExist = False
        # NameLow = Name.lower()
        # leaves = SalaryPeriod.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)
        # for leave in leaves:
        #     name = leave.Name
        #     A_Name = name.lower()
        #     if NameLow == A_Name:
        #         is_nameExist = True

        employee_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)
        category_instance = None
        if Category.objects.filter(pk=CategoryId).exists():
            category_instance = Category.objects.get(pk=CategoryId)

        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            leave_instance = Leave.objects.create(
                LeaveID=LeaveID,
                BranchID=BranchID,

                FinancialYear=FinancialYear,
                PreviousYear=PreviousYear,
                Type=Type,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                EmployeeId=employee_instance,
                EmployeeCode=EmployeeCode,
                CategoryId=category_instance,
                Balance=Balance,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            Leave_Log.objects.create(
                BranchID=BranchID,
                LeaveID=LeaveID,

                FinancialYear=FinancialYear,
                PreviousYear=PreviousYear,
                Type=Type,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                EmployeeId=employee_instance,
                EmployeeCode=EmployeeCode,
                CategoryId=category_instance,
                Balance=Balance,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            for i in LeaveDetails_list:
                print(i['LeaveTypeID'], "UVAIS")
                LeaveTypeID = i['LeaveTypeID']
                instance = None
                if LeaveType.objects.filter(LeaveTypeID=LeaveTypeID).exists():
                    instance = LeaveType.objects.get(LeaveTypeID=LeaveTypeID)
                    # if instance.ExpressionType == "Formula":
                    #     print(basicsalary_instance.ExpressionValue,"1111111111")
                    #     print(instance.ExpressionValue,"2222222222")
                    #     Amount = int(basicsalary_instance.ExpressionValue) * int(instance.ExpressionValue)/100
                    # else:
                    #     Amount = instance.ExpressionValue
                    LeaveDetails.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,

                        LeaveID=leave_instance,
                        LeaveTypeID=instance,
                        Type=instance.Type,
                        Days=i['Days'],

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )
                    LeaveDetails_Log.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,


                        LeaveID=leave_instance,
                        LeaveTypeID=instance,
                        Type=instance.Type,
                        Days=i['Days'],

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )

            data = {"LeaveID": LeaveID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Leave Name Already Exist!!!"
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
def edit_leave(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveSerializer(data=request.data)
    instance = Leave.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LeaveID = instance.LeaveID
    # instancename = instance.Name
    if serialized.is_valid():
        FinancialYear = serialized.data['FinancialYear']
        PreviousYear = serialized.data['PreviousYear']
        Type = serialized.data['Type']
        DepartmentID = serialized.data['DepartmentID']
        DesignationID = serialized.data['DesignationID']
        Balance = serialized.data['Balance']
        EmployeeCode = serialized.data['EmployeeCode']

        CategoryId = None
        EmployeeId = None
        EmployeeCode = None
        if Type == "Category":
            CategoryId = serialized.data['CategoryId']
        else:
            EmployeeId = serialized.data['EmployeeId']
            print(EmployeeId, "ULLIL")
            EmployeeCode = serialized.data['EmployeeCode']

        print(CategoryId, 'CategoryId')

        Action = 'M'
        is_nameExist = False
        leave_ok = True

        if leave_ok:
            employee_instance = None
            category_instance = None
            basicsalary_instance = None

            instance.Type = Type
            instance.FinancialYear = FinancialYear
            instance.PreviousYear = PreviousYear

            instance.DesignationID = DesignationID
            instance.DepartmentID = DepartmentID
            if Employee.objects.filter(pk=EmployeeId).exists():
                employee_instance = Employee.objects.get(pk=EmployeeId)
                instance.EmployeeId = employee_instance
            else:
                instance.EmployeeId = EmployeeId

            if Category.objects.filter(pk=CategoryId).exists():
                category_instance = Category.objects.get(pk=CategoryId)
                instance.CategoryId = category_instance
            else:
                instance.CategoryId = CategoryId
            instance.EmployeeCode = EmployeeCode
            print(Balance, 'BalanceBalanceBalanceBalance')
            instance.Balance = Balance

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Leave_Log.objects.create(
                BranchID=BranchID,

                LeaveID=LeaveID,

                FinancialYear=FinancialYear,
                PreviousYear=PreviousYear,
                Type=Type,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                EmployeeId=employee_instance,
                EmployeeCode=EmployeeCode,
                CategoryId=category_instance,
                Balance=Balance,


                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            deleted_datas = data["deleted_data"]
            print(deleted_datas)
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['LeaveDetailsID']
                    # SalesDetailsID_Deleted = deleted_Data['SalesDetailsID']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if LeaveDetails.objects.filter(pk=deleted_pk).exists():
                            deleted_detail = LeaveDetails.objects.filter(
                                pk=deleted_pk)
                            deleted_detail.delete()

            LeaveDetails_list = data['LeaveDetails']

            for i in LeaveDetails_list:
                print(i, "HALOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO&*&*&")
                detailID = i['detailID']
                if detailID == 0:
                    LeaveTypeID = i['LeaveTypeID']
                    Days = i['Days']
                    pk = i['id']
                    leavetype_instance = None
                    if LeaveType.objects.filter(pk=LeaveTypeID).exists():
                        leavetype_instance = LeaveType.objects.get(
                            pk=LeaveTypeID)
                    print(instance, "OUUUUUUUUUUUUUUUUUUUUUTTTTTTTTTTTTTTTTTTTTT", pk)
                    leaveDetail_instance = LeaveDetails.objects.get(pk=pk)
                    leaveDetail_instance.LeaveTypeID = leavetype_instance
                    leaveDetail_instance.Days = Days

                    leaveDetail_instance.save()

                elif detailID == 1:
                    print("KAYARYYYYYYYYYYYYY")
                    print(i['LeaveTypeID'], "UVAIS")
                    pk = i['LeaveTypeID']
                    leavetype_instance = None
                    if LeaveType.objects.filter(pk=pk).exists():
                        leavetype_instance = LeaveType.objects.get(pk=pk)

                    LeaveDetails.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,

                        LeaveID=instance,
                        LeaveTypeID=leavetype_instance,
                        Type=leavetype_instance.Type,
                        Days=i['Days'],

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )
                    LeaveDetails_Log.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,


                        LeaveID=instance,
                        LeaveTypeID=leavetype_instance,
                        Type=leavetype_instance.Type,
                        Days=i['Days'],

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )

            data = {"LeaveID": LeaveID}
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
def leaves(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Leave.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Leave.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LeaveRestSerializer(instances, many=True)
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
def leave(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Leave.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Leave.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LeaveSingleSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Leave Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_leave(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Leave.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Leave.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LeaveID = instance.LeaveID

        Action = "D"

        Leave_Log.objects.create(
            BranchID=BranchID,

            LeaveID=LeaveID,
            FinancialYear=instance.FinancialYear,
            PreviousYear=instance.PreviousYear,
            Type=instance.Type,
            DepartmentID=instance.DepartmentID,
            DesignationID=instance.DesignationID,
            EmployeeId=instance.EmployeeId,
            EmployeeCode=instance.EmployeeCode,
            CategoryId=instance.CategoryId,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )
        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Leave Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Leave Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
