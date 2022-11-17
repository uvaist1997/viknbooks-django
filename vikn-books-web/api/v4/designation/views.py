from brands.models import Designation, Designation_Log, Department, Department_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.designation.serializers import DesignationSerializer, DesignationRestSerializer, DepartmentSerializer, DepartmentRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.designation.functions import generate_serializer_errors
from rest_framework import status
from api.v4.designation.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_designation(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DesignationSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        DesignationName = serialized.data['DesignationName']
        Notes = serialized.data['Notes']

        Action = 'A'

        DesignationID = get_auto_id(Designation, BranchID, CompanyID)
        is_nameExist = False
        DesignationNameLow = DesignationName.lower()
        designations = Designation.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for designation in designations:
            designation_name = designation.DesignationName
            designationName = designation_name.lower()
            if DesignationNameLow == designationName:
                is_nameExist = True

        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            Designation.objects.create(
                DesignationID=DesignationID,
                BranchID=BranchID,
                DesignationName=DesignationName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            Designation_Log.objects.create(
                BranchID=BranchID,
                TransactionID=DesignationID,
                DesignationName=DesignationName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"DesignationID": DesignationID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Designation Name Already Exist!!!"
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
def edit_designation(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DesignationSerializer(data=request.data)
    instance = Designation.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    DesignationID = instance.DesignationID
    instanceDesignationname = instance.DesignationName
    if serialized.is_valid():
        DesignationName = serialized.data['DesignationName']
        Notes = serialized.data['Notes']
        Action = 'M'
        is_nameExist = False
        designation_ok = False

        DesignationNameLow = DesignationName.lower()

        designations = Designation.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for designation in designations:
            designation_name = designation.DesignationName

            designationName = designation_name.lower()

            if DesignationNameLow == designationName:
                is_nameExist = True

            if instanceDesignationname.lower() == DesignationNameLow:

                designation_ok = True

        if designation_ok:

            instance.DesignationName = DesignationName
            instance.Notes = Notes
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Designation_Log.objects.create(
                BranchID=BranchID,
                TransactionID=DesignationID,
                DesignationName=DesignationName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"DesignationID": DesignationID}
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
                    "message": "Designation Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.DesignationName = DesignationName
                instance.Notes = Notes
                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                Designation_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=DesignationID,
                    DesignationName=DesignationName,
                    Notes=Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"DesignationID": DesignationID}
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
def designations(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Designation.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Designation.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = DesignationRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Designation Not Found in this BranchID!"
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
def designation(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Designation.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Designation.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = DesignationRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Designation Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_designation(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Designation.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Designation.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        DesignationID = instance.DesignationID
        DesignationName = instance.DesignationName
        Notes = instance.Notes
        Action = "D"

        instance.delete()

        Designation_Log.objects.create(
            BranchID=BranchID,
            TransactionID=DesignationID,
            DesignationName=DesignationName,
            Notes=Notes,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Designation Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Designation Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def create_department(request):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     today = datetime.datetime.now()
#     serialized = DepartmentSerializer(data=request.data)
#     if serialized.is_valid():

#         BranchID = serialized.data['BranchID']
#         DepartmentName = serialized.data['DepartmentName']
#         Notes = serialized.data['Notes']

#         Action = 'A'

#         DepartmentID = get_auto_DepartmentID(Department,BranchID,CompanyID)
#         is_nameExist = False
#         DepartmentNameLow = DepartmentName.lower()
#         departments = Department.objects.filter(BranchID=BranchID,CompanyID=CompanyID)
#         for department in departments:
#             department_name = department.DepartmentName
#             departmentName = department_name.lower()
#             if DepartmentNameLow == departmentName:
#                 is_nameExist = True

#         if not is_nameExist:
#             # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
#             Department.objects.create(
#                 DepartmentID=DepartmentID,
#                 BranchID=BranchID,
#                 DepartmentName=DepartmentName,
#                 Notes=Notes,
#                 CreatedUserID=CreatedUserID,
#                 CreatedDate=today,
#                 UpdatedDate=today,
#                 Action=Action,
#                 CompanyID=CompanyID,
#                 )

#             Department_Log.objects.create(
#                 TransactionID=DepartmentID,
#                 BranchID=BranchID,
#                 DepartmentName=DepartmentName,
#                 Notes=Notes,
#                 CreatedUserID=CreatedUserID,
#                 CreatedDate=today,
#                 UpdatedDate=today,
#                 Action=Action,
#                 CompanyID=CompanyID,
#                 )

#             data = {"DepartmentID" : DepartmentID}
#             data.update(serialized.data)
#             response_data = {
#                 "StatusCode" : 6000,
#                 "data" : data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             response_data = {
#             "StatusCode" : 6001,
#             "message" : "Department Name Already Exist!!!"
#         }

#         return Response(response_data, status=status.HTTP_200_OK)
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : generate_serializer_errors(serialized._errors)
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def edit_department(request,pk):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     today = datetime.datetime.now()
#     serialized = DepartmentSerializer(data=request.data)
#     instance = Department.objects.get(pk=pk,CompanyID=CompanyID)
#     BranchID = instance.BranchID
#     DepartmentID = instance.DepartmentID
#     instanceDepartmentName = instance.DepartmentName
#     if serialized.is_valid():
#         DepartmentName = serialized.data['DepartmentName']
#         Notes = serialized.data['Notes']
#         Action = 'M'
#         is_nameExist = False
#         department_ok = False

#         DepartmentNameLow = DepartmentName.lower()

#         departments = Department.objects.filter(BranchID=BranchID,CompanyID=CompanyID)

#         for dep in departments:
#             dep_name = dep.DepartmentName

#             depName = dep_name.lower()

#             if DepartmentNameLow == depName:
#                 is_nameExist = True

#             if instanceDepartmentName.lower() == DepartmentNameLow:

#                 department_ok = True

#         if  department_ok:

#             instance.DepartmentName = DepartmentName
#             instance.Notes = Notes
#             instance.CreatedUserID = CreatedUserID
#             instance.UpdatedDate = today
#             instance.Action = Action
#             instance.save()

#             Department_Log.objects.create(
#                 TransactionID=DepartmentID,
#                 BranchID=BranchID,
#                 DepartmentName=DepartmentName,
#                 Notes=Notes,
#                 CreatedUserID=CreatedUserID,
#                 CreatedDate=today,
#                 UpdatedDate=today,
#                 Action=Action,
#                 CompanyID=CompanyID,
#                 )

#             data = {"DepartmentID" : DepartmentID}
#             data.update(serialized.data)
#             response_data = {
#                 "StatusCode" : 6000,
#                 "data" : data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         else:


#             if is_nameExist:

#                 response_data = {
#                     "StatusCode" : 6001,
#                     "message" : "Department Name Already exist with this Branch"
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)

#             else:
#                 instance.DepartmentName = DepartmentName
#                 instance.Notes = Notes
#                 instance.CreatedUserID = CreatedUserID
#                 instance.UpdatedDate = today
#                 instance.Action = Action
#                 instance.save()

#                 Department_Log.objects.create(
#                     TransactionID=DepartmentID,
#                     BranchID=BranchID,
#                     DepartmentName=DepartmentName,
#                     Notes=Notes,
#                     CreatedUserID=CreatedUserID,
#                     CreatedDate=today,
#                     UpdatedDate=today,
#                     Action=Action,
#                     CompanyID=CompanyID,
#                     )

#                 data = {"DepartmentID" : DepartmentID}
#                 data.update(serialized.data)
#                 response_data = {
#                     "StatusCode" : 6000,
#                     "data" : data
#                 }

#                 return Response(response_data, status=status.HTTP_200_OK)

#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : generate_serializer_errors(serialized._errors)
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def departments(request):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     serialized1 = ListSerializer(data=request.data)
#     if serialized1.is_valid():
#         BranchID = serialized1.data['BranchID']
#         if Department.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
#             instances = Department.objects.filter(BranchID=BranchID,CompanyID=CompanyID)
#             serialized = DepartmentRestSerializer(instances,many=True)
#             response_data = {
#                 "StatusCode" : 6000,
#                 "data" : serialized.data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             response_data = {
#             "StatusCode" : 6001,
#             "message" : "Department Not Found in this Branch!"
#             }

#             return Response(response_data, status=status.HTTP_200_OK)
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : "Branch ID You Enterd is not Valid!!!"
#         }

#         return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def department(request,pk):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     instance = None
#     if Department.objects.filter(pk=pk,CompanyID=CompanyID).exists():
#         instance = Department.objects.get(pk=pk,CompanyID=CompanyID)
#         serialized = DepartmentRestSerializer(instance)
#         response_data = {
#             "StatusCode" : 6000,
#             "data" : serialized.data
#         }
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : "Department Not Found!"
#         }

#     return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def delete_department(request,pk):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     CreatedUserID = data['CreatedUserID']

#     today = datetime.datetime.now()
#     instance = None
#     if Department.objects.filter(pk=pk,CompanyID=CompanyID).exists():
#         instance = Department.objects.get(pk=pk,CompanyID=CompanyID)
#         Action = "D"
#         Department_Log.objects.create(
#             TransactionID=instance.DepartmentID,
#             BranchID=instance.BranchID,
#             DepartmentName=instance.DepartmentName,
#             Notes=instance.Notes,
#             CreatedUserID=CreatedUserID,
#             CreatedDate=today,
#             UpdatedDate=today,
#             Action=Action,
#             CompanyID=CompanyID,
#             )

#         instance.delete()
#         response_data = {
#             "StatusCode" : 6000,
#             "message" : "Department Deleted Successfully!"
#         }
#     else:
#         response_data = {
#             "StatusCode" : 6001,
#             "message" : "Department Not Found!"
#         }

#     return Response(response_data, status=status.HTTP_200_OK)
