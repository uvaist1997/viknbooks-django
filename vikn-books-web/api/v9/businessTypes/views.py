from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v9.businessTypes.functions import generate_serializer_errors
from api.v9.businessTypes.serializers import BusinessTypeSerializer
from brands.models import BusinessType


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_business_type(request):
    serializer = BusinessTypeSerializer(data=request.data)
    if serializer.is_valid():
        Name = serializer.data["Name"]
        Name = Name.title()
        if BusinessType.objects.filter(Name__iexact=Name):
            response_data = {
                "StatusCode": 6001,
                "message": "Business Type Already Exist!!!",
            }
        else:
            BusinessType.objects.create(
                Name=Name,
            )
            response_data = {"StatusCode": 6000, "data": serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serializer._errors),
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_business_type(request, pk):
    serializer = BusinessTypeSerializer(data=request.data)
    instance = BusinessType.objects.get(pk=pk)

    if serializer.is_valid():
        Name = serializer.data["Name"]
        Name = Name.title()
        existing = BusinessType.objects.exclude(Name__in=[instance.Name])
        if existing.filter(Name__iexact=Name):
            response_data = {
                "StatusCode": 6001,
                "message": "Business Type Already Exist",
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
            "message": generate_serializer_errors(serializer._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def business_types(request):
    instances = None
    if BusinessType.objects.all().exists():
        instances = BusinessType.objects.all()
        serializer = BusinessTypeSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serializer.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Business Type Not Found"}
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def business_type(request, pk):
    instance = None
    if BusinessType.objects.filter(pk=pk).exists():
        instance = BusinessType.objects.get(pk=pk)
        serializer = BusinessTypeSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serializer.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Business Type Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_business_type(request, pk):
    instance = None
    if BusinessType.objects.filter(pk=pk).exists():
        instance = BusinessType.objects.get(pk=pk)
        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "Business Type Deleted Successfully!",
        }
    else:
        response_data = {"StatusCode": 6001, "message": "Business Type Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)
