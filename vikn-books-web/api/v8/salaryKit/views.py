from brands.models import SalaryKit, SalaryKit_Log, Employee, Category, SalaryComponent, SalaryKitDetails, SalaryKitDetails_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.salaryKit.serializers import SalaryKitSerializer, SalaryKitSingleSerializer, SalaryKitRestSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.salaryKit.functions import generate_serializer_errors
from rest_framework import status
from api.v8.salaryKit.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_salaryKit(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryKitSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        Type = serialized.data['Type']
        Date = serialized.data['Date']
        DesignationID = serialized.data['DesignationID']
        DepartmentID = serialized.data['DepartmentID']

        BasicSalaryId = serialized.data['BasicSalaryId']
        # BasicSalaryAmount = serialized.data['BasicSalaryAmount']
        EmployeeId = serialized.data['EmployeeId']
        EmployeeCode = serialized.data['EmployeeCode']
        SalaryFreequency = serialized.data['SalaryFreequency']
        SalaryComponentType = serialized.data['SalaryComponentType']
        CategoryId = None
        EmployeeId = None
        if Type == "Category":
            CategoryId = serialized.data['CategoryId']
        else:
            EmployeeId = serialized.data['EmployeeId']

        print(CategoryId, "CategoryId")

        SalaryKitDetails_list = data['SalaryKitDetails']

        try:
            EmployeeCode = serialized.data['EmployeeCode']
        except:
            EmployeeCode = 0

        Action = 'A'
        SalaryKitID = get_auto_id(SalaryKit, BranchID, CompanyID)
        is_nameExist = False
        # NameLow = Name.lower()
        # salarykits = SalaryKit.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)
        # for salarykit in salarykits:
        #     name = salarykit.Name
        #     A_Name = name.lower()
        #     if NameLow == A_Name:
        #         is_nameExist = True

        employee_instance = None
        if Employee.objects.filter(pk=EmployeeId).exists():
            employee_instance = Employee.objects.get(pk=EmployeeId)
        category_instance = None
        if Category.objects.filter(pk=CategoryId).exists():
            category_instance = Category.objects.get(pk=CategoryId)

        basicsalary_instance = None
        if SalaryComponent.objects.filter(pk=BasicSalaryId).exists():
            basicsalary_instance = SalaryComponent.objects.get(
                pk=BasicSalaryId)

        print(Date, 'Date')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            SalaryKit.objects.create(
                SalaryKitID=SalaryKitID,
                BranchID=BranchID,

                Date=Date,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                EmployeeId=employee_instance,
                CategoryId=category_instance,
                BasicSalaryId=basicsalary_instance,
                EmployeeCode=EmployeeCode,
                Type=Type,
                SalaryFreequency=SalaryFreequency,
                SalaryComponentType=SalaryComponentType,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            SalaryKit_Log.objects.create(
                BranchID=BranchID,
                SalaryKitID=SalaryKitID,

                Date=Date,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                EmployeeId=employee_instance,
                CategoryId=category_instance,
                BasicSalaryId=basicsalary_instance,
                EmployeeCode=EmployeeCode,
                Type=Type,
                SalaryFreequency=SalaryFreequency,
                SalaryComponentType=SalaryComponentType,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            for i in SalaryKitDetails_list:
                print(i['SalaryComponentID'], "UVAIS")
                SalaryComponentID = i['SalaryComponentID']
                instance = None
                if SalaryComponent.objects.filter(SalaryComponentID=SalaryComponentID).exists():
                    instance = SalaryComponent.objects.get(
                        SalaryComponentID=SalaryComponentID)
                    if instance.ExpressionType == "Formula":
                        print(basicsalary_instance.ExpressionValue, "1111111111")
                        print(instance.ExpressionValue, "2222222222")
                        Amount = int(basicsalary_instance.ExpressionValue) * \
                            int(instance.ExpressionValue)/100
                    else:
                        Amount = instance.ExpressionValue
                    SalaryKitDetails.objects.create(
                        SalaryKitID=SalaryKitID,
                        SalaryComponentID=instance,
                        ComponentType=instance.ComponentType,
                        ExpressionType=instance.ExpressionType,
                        Amount=Amount,

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )
                    SalaryKitDetails_Log.objects.create(
                        SalaryKitID=SalaryKitID,
                        SalaryComponentID=instance,
                        ComponentType=instance.ComponentType,
                        ExpressionType=instance.ExpressionType,
                        Amount=Amount,

                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,

                    )

            data = {"SalaryKitID": SalaryKitID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "SalaryKit Name Already Exist!!!"
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
def edit_salaryKit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalaryKitSerializer(data=request.data)
    instance = SalaryKit.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    SalaryKitID = instance.SalaryKitID
    # instancename = instance.Name
    if serialized.is_valid():
        Type = serialized.data['Type']
        Date = serialized.data['Date']
        DesignationID = serialized.data['DesignationID']
        DepartmentID = serialized.data['DepartmentID']

        BasicSalaryId = serialized.data['BasicSalaryId']
        # BasicSalaryAmount = serialized.data['BasicSalaryAmount']
        SalaryFreequency = serialized.data['SalaryFreequency']
        SalaryComponentType = serialized.data['SalaryComponentType']

        EmployeeId = serialized.data['EmployeeId']
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
        # try:
        #     CategoryId = serialized.data['Category']
        # except:
        #     CategoryId = None

        # try:
        #     EmployeeId = serialized.data['EmployeeId']
        # except:
        #     EmployeeId = None

        Action = 'M'
        is_nameExist = False
        salarykit_ok = True

        # NameLow = Name.lower()

        # salarykits = SalaryKit.objects.filter(
        #     BranchID=BranchID, CompanyID=CompanyID)

        # for salarykit in salarykits:
        #     name = salarykit.Name

        #     salarykitName = name.lower()

        #     if NameLow == salarykitName:
        #         is_nameExist = True

        #     if instancename.lower() == NameLow:

        #         salarykit_ok = True

        if salarykit_ok:
            employee_instance = None
            category_instance = None
            basicsalary_instance = None

            instance.Type = Type
            instance.Date = Date
            instance.DesignationID = DesignationID
            instance.DepartmentID = DepartmentID
            if SalaryComponent.objects.filter(pk=BasicSalaryId).exists():
                basicsalary_instance = SalaryComponent.objects.get(
                    pk=BasicSalaryId)
                instance.BasicSalaryId = basicsalary_instance
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
            instance.SalaryFreequency = SalaryFreequency
            instance.SalaryComponentType = SalaryComponentType

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            SalaryKit_Log.objects.create(
                BranchID=BranchID,

                SalaryKitID=SalaryKitID,

                Date=Date,
                DesignationID=DesignationID,
                DepartmentID=DepartmentID,
                EmployeeId=employee_instance,
                CategoryId=category_instance,
                BasicSalaryId=basicsalary_instance,
                EmployeeCode=EmployeeCode,
                Type=Type,
                SalaryFreequency=SalaryFreequency,
                SalaryComponentType=SalaryComponentType,


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
                    deleted_pk = deleted_Data['SalaryKitDetailsID']
                    # SalesDetailsID_Deleted = deleted_Data['SalesDetailsID']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if SalaryKitDetails.objects.filter(pk=deleted_pk).exists():
                            deleted_detail = SalaryKitDetails.objects.filter(
                                pk=deleted_pk)
                            deleted_detail.delete()

            SalaryKitDetails_list = data['SalaryKitDetails']

            for i in SalaryKitDetails_list:
                print("HALOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO&*&*&")
                detailID = i['detailID']
                if detailID == 0:
                    SalaryComponentID = i['SalaryComponentID']
                    pk = i['id']
                    salary_instance = None
                    if SalaryComponent.objects.filter(pk=SalaryComponentID).exists():
                        salary_instance = SalaryComponent.objects.get(
                            pk=SalaryComponentID)
                    print(instance, "OUUUUUUUUUUUUUUUUUUUUUTTTTTTTTTTTTTTTTTTTTT")
                    salaryKitDetail_instance = SalaryKitDetails.objects.get(
                        pk=pk)
                    salaryKitDetail_instance.SalaryComponentID = salary_instance
                    salaryKitDetail_instance.ExpressionType = salary_instance.ExpressionType
                    salaryKitDetail_instance.ComponentType = salary_instance.ComponentType

                    Amount = int(instance.BasicSalaryId.ExpressionValue) * \
                        int(salary_instance.ExpressionValue)/100
                    salaryKitDetail_instance.Amount = Amount
                    salaryKitDetail_instance.save()

                elif detailID == 1:
                    print("KAYARYYYYYYYYYYYYY")
                    print(i['SalaryComponentID'], "UVAIS")
                    pk = i['SalaryComponentID']
                    salary_instance = None
                    if SalaryComponent.objects.filter(pk=pk).exists():
                        salary_instance = SalaryComponent.objects.get(pk=pk)
                        if salary_instance.ExpressionType == "Formula":
                            print(instance.BasicSalaryId.ExpressionValue,
                                  "1111111111")
                            print(salary_instance.ExpressionValue, "2222222222")
                            Amount = int(instance.BasicSalaryId.ExpressionValue) * \
                                int(salary_instance.ExpressionValue)/100
                        else:
                            Amount = salary_instance.ExpressionValue
                        SalaryKitDetails.objects.create(
                            SalaryKitID=SalaryKitID,
                            SalaryComponentID=salary_instance,
                            ComponentType=salary_instance.ComponentType,
                            ExpressionType=salary_instance.ExpressionType,
                            Amount=Amount,

                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,

                        )
                        SalaryKitDetails_Log.objects.create(
                            SalaryKitID=SalaryKitID,
                            SalaryComponentID=salary_instance,
                            ComponentType=salary_instance.ComponentType,
                            ExpressionType=salary_instance.ExpressionType,
                            Amount=Amount,

                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,

                        )

            data = {"SalaryKitID": SalaryKitID}
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
def salaryKits(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalaryKit.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = SalaryKit.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = SalaryKitRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Kit Not Found in this BranchID!"
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
def salaryKit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if SalaryKit.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryKit.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = SalaryKitSingleSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Kit Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_salaryKit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalaryKit.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = SalaryKit.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        SalaryKitID = instance.SalaryKitID
        # Name = instance.Name

        Action = "D"

        SalaryKit_Log.objects.create(
            BranchID=BranchID,
            SalaryKitID=SalaryKitID,

            Date=instance.Date,
            DesignationID=instance.DesignationID,
            DepartmentID=instance.DepartmentID,
            EmployeeId=instance.EmployeeId,
            CategoryId=instance.CategoryId,
            BasicSalaryId=instance.BasicSalaryId,
            EmployeeCode=instance.EmployeeCode,
            Type=instance.Type,
            SalaryFreequency=instance.SalaryFreequency,
            SalaryComponentType=instance.SalaryComponentType,

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )
        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Salary Kit Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Kit Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
