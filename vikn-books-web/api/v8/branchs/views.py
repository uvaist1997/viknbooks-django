from brands.models import Branch, Branch_Log, Country, State
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.branchs.serializers import BranchSerializer, BranchRestSerializer
from api.v8.branchs.functions import generate_serializer_errors
from rest_framework import status
from api.v8.branchs.functions import get_auto_id
from main.functions import get_company
import datetime
from main.functions import get_company, activity_log


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_branch(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BranchSerializer(data=request.data)
    if serialized.is_valid():

        BranchName = serialized.data['BranchName']
        regional_office_pk = serialized.data['regional_office']
        Phone = serialized.data['Phone']
        Email = serialized.data['Email']
        Building = serialized.data['Building']
        City = serialized.data['City']
        state_pk = serialized.data['state']
        country_pk = serialized.data['country']
        GSTNumber = serialized.data['GSTNumber']
        VATNumber = serialized.data['VATNumber']
        is_gst = serialized.data['is_gst']
        is_vat = serialized.data['is_vat']
        is_regional_office = serialized.data['is_regional_office']

        if state_pk:
            state = State.objects.get(pk=state_pk)

        if country_pk:
            country = Country.objects.get(pk=country_pk)

        regional_office = None
        if regional_office_pk:
            regional_office = Branch.objects.get(pk=regional_office_pk)

        Action = "A"

        BranchID = get_auto_id(Branch, CompanyID)

        Branch.objects.create(
            BranchID=BranchID,
            BranchName=BranchName,
            regional_office=regional_office,
            Phone=Phone,
            Email=Email,
            Building=Building,
            City=City,
            state=state,
            country=country,
            GSTNumber=GSTNumber,
            VATNumber=VATNumber,
            is_gst=is_gst,
            is_vat=is_vat,
            is_regional_office=is_regional_office,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        Branch_Log.objects.create(
            TransactionID=BranchID,
            BranchName=BranchName,
            regional_office=regional_office,
            Phone=Phone,
            Email=Email,
            Building=Building,
            City=City,
            state=state,
            country=country,
            GSTNumber=GSTNumber,
            VATNumber=VATNumber,
            is_gst=is_gst,
            is_vat=is_vat,
            is_regional_office=is_regional_office,
            Action=Action,
            CreatedUserID=CreatedUserID,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        data = {"BranchID": BranchID}
        data.update(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Create',
                     'Branch created failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BranchSerializer(data=request.data)
    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)

    if instance:
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

        Action = "M"

        instance.Action = Action
        instance.CreatedUserID = CreatedUserID
        instance.UpdatedDate = today
        instance.save()
        if serialized.is_valid():
            BranchName = serialized.data['BranchName']
            RegionalOffice = serialized.data['RegionalOffice']
            Phone = serialized.data['Phone']
            Email = serialized.data['Email']
            Building = serialized.data['Building']
            City = serialized.data['City']
            state = serialized.data['State']
            country = serialized.data['Country']
            GSTNumber = serialized.data['GSTNumber']
            VATNumber = serialized.data['VATNumber']
            is_gst = serialized.data['is_gst']
            is_vat = serialized.data['is_vat']
            is_regional_office = serialized.data['is_regional_office']

            serialized.update(instance, serialized.data)
            Branch_Log.objects.create(
                TransactionID=BranchID,
                BranchName=BranchName,
                RegionalOffice=RegionalOffice,
                Phone=Phone,
                Email=Email,
                Building=Building,
                City=City,
                state=state,
                country=country,
                GSTNumber=GSTNumber,
                VATNumber=VATNumber,
                is_gst=is_gst,
                is_vat=is_vat,
                is_regional_office=is_regional_office,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Edit',
                         'Branch Updated failed.', generate_serializer_errors(serialized._errors))
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Edit', 'Branch Updated failed.', "Branch Not Found!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def regional_office_branchs(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Branch.objects.filter(
        CompanyID=CompanyID, is_regional_office=True)
    serialized = BranchRestSerializer(instances, many=True)
    #request , company, log_type, user, source, action, message, description

    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def branchs(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Branch.objects.filter(CompanyID=CompanyID)
    serialized = BranchRestSerializer(instances, many=True)
    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                 'Branch', 'List VIew', 'Branch List Viewed.', "Branch List Viewed.")
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = BranchRestSerializer(instance)
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed.', 'Branch Single Page Viewed.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    if selecte_ids:
        if Branch.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Branch.objects.filter(pk__in=selecte_ids)
    else:
        if Branch.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Branch.objects.filter(pk=pk)

    if instances:
        for instance in instances:

            state = State.objects.get(pk=instance.state.pk)
            country = Country.objects.get(pk=instance.country.pk)
            BranchID = instance.BranchID
            BranchName = instance.BranchName
            regional_office = None
            if instance.regional_office:
                regional_office = instance.regional_office.pk,
            Phone = instance.Phone,
            Email = instance.Email,
            Building = instance.Building,
            City = instance.City,
            GSTNumber = instance.GSTNumber,
            VATNumber = instance.VATNumber,
            is_gst = instance.is_gst,
            is_vat = instance.is_vat,
            is_regional_office = instance.is_regional_office,
            Action = "D"

            instance.delete()

            Branch_Log.objects.create(
                TransactionID=BranchID,
                BranchName=BranchName,
                regional_office=regional_office,
                Phone=Phone,
                Email=Email,
                Building=Building,
                City=City,
                state=state,
                country=country,
                GSTNumber=GSTNumber,
                VATNumber=VATNumber,
                is_gst=is_gst,
                is_vat=is_vat,
                is_regional_office=is_regional_office,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                         'Deleted', "Branch Deleted Successfully!", "Branch Deleted Successfully!")
            response_data = {
                "StatusCode": 6000,
                "message": "Branch Deleted Successfully!"
            }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Delete', 'Branch Deleted Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @renderer_classes((JSONRenderer,))
# def get_batch_value(request):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     BranchID = data['BranchID']

#     if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
#         check_EnableProductBatchWise = GeneralSettings.objects.get(
#             CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
#     if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:

#     response_data = {
#         "StatusCode": 6000
#     }

#     return Response(response_data, status=status.HTTP_200_OK)
