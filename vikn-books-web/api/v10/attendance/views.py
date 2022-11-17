import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.attendance.functions import (
    generate_serializer_errors,
    get_auto_DepartmentID,
    get_auto_id,
)
from api.v10.attendance.serializers import (
    AttendanceDetailSerializer,
    AttendanceMasterRestSerializer,
    AttendanceMasterSerializer,
    AttendanceSingleSerializer,
)
from api.v10.brands.serializers import ListSerializer
from brands.models import (
    AttendanceDetail,
    AttendanceDetail_Log,
    AttendanceMaster,
    AttendanceMaster_Log,
    Category,
    Employee,
)
from main.functions import get_company


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_attendance(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = AttendanceMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data["BranchID"]

        Shift = serialized.data["Shift"]
        Date = data["Date"]
        DepartmentID = serialized.data["DepartmentID"]
        DesignationID = serialized.data["DesignationID"]
        CategoryId = serialized.data["CategoryId"]
        AttendanceDetails_list = data["AttendanceDetails"]
        print(Date, "MUNNE")

        Date_str = str(Date) + " 08:15:27.243860"
        Date = datetime.datetime.strptime(Date_str, "%Y-%m-%d %H:%M:%S.%f")
        # category_instance = None
        print(Date, "Pinne")
        if Category.objects.filter(pk=CategoryId).exists():
            CategoryId = Category.objects.get(pk=CategoryId)
        else:
            CategoryId = None

        Action = "A"
        AttendanceMasterID = get_auto_id(AttendanceMaster, BranchID, CompanyID)
        is_nameExist = False
        # NameLow = Name.lower()
        # Attendances = AttendanceMaster.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)
        # for Attendance in Attendances:
        #     name = Attendance.Name
        #     A_Name = name.lower()
        #     if NameLow == A_Name:
        #         is_nameExist = True

        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            master_instance = AttendanceMaster.objects.create(
                AttendanceMasterID=AttendanceMasterID,
                BranchID=BranchID,
                Shift=Shift,
                Date=Date,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                CategoryId=CategoryId,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            AttendanceMaster_Log.objects.create(
                BranchID=BranchID,
                AttendanceMasterID=AttendanceMasterID,
                Shift=Shift,
                Date=Date,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                CategoryId=CategoryId,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )
            for i in AttendanceDetails_list:
                # detail_serialized = AttendanceDetailSerializer(data=i)
                # if detail_serialized.is_valid():
                ShiftStartTime = i["ShiftStartTime"]
                print(i, "AttendanceDetail", ShiftStartTime)
                pk = i["Employeepk"]
                ShiftStartTime = i["ShiftStartTime"]
                ShiftEndTime = i["ShiftEndTime"]
                Status = i["Status"]
                instance = None
                if Employee.objects.filter(pk=pk).exists():
                    instance = Employee.objects.get(pk=pk)

                    AttendanceDetail.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        AttendanceId=master_instance,
                        EmployeeId=instance,
                        EmployeeCode=instance.EmployeeCode,
                        Status=Status,
                        ShiftStartTime=ShiftStartTime,
                        ShiftEndTime=ShiftEndTime,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                    )
                    AttendanceDetail_Log.objects.create(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        AttendanceId=master_instance,
                        EmployeeId=instance,
                        EmployeeCode=instance.EmployeeCode,
                        Status=Status,
                        ShiftStartTime=ShiftStartTime,
                        ShiftEndTime=ShiftEndTime,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                    )
                # else:
                #     response_data = {
                #         "StatusCode": 6001,
                #         "message": generate_serializer_errors(detail_serialized._errors)
                #     }

                #     return Response(response_data, status=status.HTTP_200_OK)

            data = {"AttendanceMasterID": AttendanceMasterID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Period Name Already Exist!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_attendance(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = AttendanceMasterSerializer(data=request.data)
    instance = AttendanceMaster.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    AttendanceMasterID = instance.AttendanceMasterID
    if serialized.is_valid():
        Shift = serialized.data["Shift"]
        Date = data["Date"]
        DepartmentID = serialized.data["DepartmentID"]
        DesignationID = serialized.data["DesignationID"]
        CategoryId = serialized.data["CategoryId"]
        AttendanceDetails_list = data["AttendanceDetails"]

        Action = "M"
        is_nameExist = False
        attendance_ok = True

        # NameLow = Name.lower()

        # Attendances = AttendanceMaster.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for Attendance in Attendances:
        #     name = Attendance.Name

        #     AttendanceName = name.lower()

        #     if NameLow == AttendanceName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         attendance_ok = True

        if attendance_ok:
            category_instance = None

            instance.Shift = Shift
            instance.Date = Date
            instance.DesignationID = DesignationID
            instance.DepartmentID = DepartmentID

            if Category.objects.filter(pk=CategoryId).exists():
                category_instance = Category.objects.get(pk=CategoryId)
                instance.CategoryId = category_instance

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            AttendanceMaster_Log.objects.create(
                BranchID=BranchID,
                AttendanceMasterID=AttendanceMasterID,
                Shift=Shift,
                Date=Date,
                DepartmentID=DepartmentID,
                DesignationID=DesignationID,
                CategoryId=category_instance,
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
                    deleted_pk = deleted_Data["AttendanceDetailsID"]
                    # SalesDetailsID_Deleted = deleted_Data['SalesDetailsID']

                    if not deleted_pk == "" or not deleted_pk == 0:
                        if AttendanceDetail.objects.filter(pk=deleted_pk).exists():
                            deleted_detail = AttendanceDetail.objects.filter(
                                pk=deleted_pk
                            )
                            deleted_detail.delete()

            AttendanceDetails_list = data["AttendanceDetails"]
            for i in AttendanceDetails_list:
                print("HALOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO&*&*&")
                detailID = i["detailID"]
                if detailID == 0:
                    EmployeeID = i["EmployeeId"]
                    Status = i["Status"]
                    ShiftStartTime = i["ShiftStartTime"]
                    ShiftEndTime = i["ShiftEndTime"]
                    pk = i["id"]
                    employee_instance = None
                    if Employee.objects.filter(pk=EmployeeID).exists():
                        employee_instance = Employee.objects.get(pk=EmployeeID)
                    print(instance, "OUUUUUUUUUUUUUUUUUUUUUTTTTTTTTTTTTTTTTTTTTT")
                    attendanceDetail_instance = AttendanceDetail.objects.get(pk=pk)
                    attendanceDetail_instance.EmployeeID = employee_instance
                    attendanceDetail_instance.EmployeeCode = (
                        employee_instance.EmployeeCode
                    )
                    attendanceDetail_instance.Status = Status
                    attendanceDetail_instance.ShiftStartTime = ShiftStartTime
                    attendanceDetail_instance.ShiftEndTime = ShiftEndTime
                    attendanceDetail_instance.save()

                elif detailID == 1:
                    print(i, "KAYARYYYYYYYYYYYYY")
                    print(i["Employeepk"], "UVAIS")
                    pk = i["Employeepk"]
                    Status = i["Status"]
                    ShiftStartTime = i["ShiftStartTime"]
                    ShiftEndTime = i["ShiftEndTime"]
                    employee_instance = None
                    if Employee.objects.filter(pk=pk).exists():
                        employee_instance = Employee.objects.get(pk=pk)

                        AttendanceDetail.objects.create(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            AttendanceId=instance,
                            EmployeeId=employee_instance,
                            EmployeeCode=employee_instance.EmployeeCode,
                            Status=Status,
                            ShiftStartTime=ShiftStartTime,
                            ShiftEndTime=ShiftEndTime,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                        )
                        AttendanceDetail_Log.objects.create(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            AttendanceId=instance,
                            EmployeeId=employee_instance,
                            EmployeeCode=employee_instance.EmployeeCode,
                            Status=Status,
                            ShiftStartTime=ShiftStartTime,
                            ShiftEndTime=ShiftEndTime,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                        )

            data = {"AttendanceMasterID": AttendanceMasterID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def attendances(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if AttendanceMaster.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID
        ).exists():
            instances = AttendanceMaster.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID
            )
            serialized = AttendanceMasterRestSerializer(instances, many=True)
            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Attendance Not Found in this BranchID!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def attendance(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    instance = None
    if AttendanceMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AttendanceMaster.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = AttendanceSingleSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Attendance Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_attendance(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    instance = None
    if AttendanceMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AttendanceMaster.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID

        Action = "D"

        instance.delete()

        AttendanceMaster_Log.objects.create(
            BranchID=BranchID,
            AttendanceMasterID=instance.AttendanceMasterID,
            Shift=instance.Shift,
            Date=instance.Date,
            DepartmentID=instance.DepartmentID,
            DesignationID=instance.DesignationID,
            CategoryId=instance.CategoryId,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Attendance Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "Salary Period Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)
