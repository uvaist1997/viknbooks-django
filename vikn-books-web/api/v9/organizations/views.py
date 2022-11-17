from brands.models import CompanySettings,Edition
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.organizations.serializers import OrganizationSettingsSerializer, OrganizationUserListSerializer, OrganizationListSerializer, OrganizationSerializer
from api.v9.organizations.functions import generate_serializer_errors
from rest_framework import status


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_organization_settings(request):
    serializer = OrganizationSettingsSerializer(data=request.data)
    data = request.data
    if serializer.is_valid():
        ExpiryDate = serializer.data['ExpiryDate']
        NoOfUsers = serializer.data['NoOfUsers']
        Customer = serializer.data['Customer']
        Organization = serializer.data['Organization']
        try:
            IsTrialVersion = serializer.data['IsTrialVersion']
        except:
            IsTrialVersion = False

        try:
            EditionName = serializer.data['EditionName']
        except:
            EditionName = "Soft Edition"

        try:
            Permission = data['Permission']
        except:
            Permission = ""

        CompanySettings.objects.filter(owner__pk=Customer, pk=Organization).update(
            ExpiryDate=ExpiryDate, NoOfUsers=NoOfUsers,IsTrialVersion=IsTrialVersion,Edition=EditionName,Permission=Permission)

        response_data = {
            "StatusCode": 6000,
            # "data" : serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serializer._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_organization(request, pk):
    serializer = CompanySettingsSerializer(data=request.data)
    instance = CompanySettings.objects.get(pk=pk)

    if serializer.is_valid():
        Name = serializer.data['Name']
        Name = Name.title()
        existing = CompanySettings.objects.exclude(Name__in=[instance.Name])
        if existing.filter(Name__iexact=Name):
            response_data = {
                "StatusCode": 6001,
                "message": "Business Type Already Exist"
            }
        else:
            instance.Name = Name
            instance.save()

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated",
            }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serializer._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


# auth user superuser = False list
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def organization_user_list(request):
    instances = None
    if User.objects.filter(is_superuser=False).exists():
        instances = User.objects.filter(is_superuser=False)
        serializer = OrganizationUserListSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Business Type Not Found"
        }
        return Response(response_data, status=status.HTTP_200_OK)

# used for filter company by users


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def organization_list(request, pk):
    instances = None
    if User.objects.filter(is_superuser=False, pk=pk).exists():
        # user_instance = User.objects.filter(is_superuser=False,pk=pk)
        company_instances = CompanySettings.objects.filter(owner__pk=pk)
        serializer = OrganizationListSerializer(company_instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Business Type Not Found"
        }
        return Response(response_data, status=status.HTTP_200_OK)

# company list


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def organizations(request):
    instances = CompanySettings.objects.all()
    serialized = OrganizationSerializer(instances, many=True)
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def business_types(request):
    instances = None
    if CompanySettings.objects.all().exists():
        instances = CompanySettings.objects.all()
        serializer = CompanySettingsSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Business Type Not Found"
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def business_type(request, pk):
    instance = None
    if CompanySettings.objects.filter(pk=pk).exists():
        instance = CompanySettings.objects.get(pk=pk)
        serializer = CompanySettingsSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serializer.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Business Type Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_business_type(request, pk):
    instance = None
    if CompanySettings.objects.filter(pk=pk).exists():
        instance = CompanySettings.objects.get(pk=pk)
        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "Business Type Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Business Type Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
