from brands.models import State, Product, Country
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.states.serializers import StateSerializer, StateRestSerializer, ListSerializer
from api.v3.states.functions import generate_serializer_errors
from rest_framework import status
from api.v3.states.functions import get_auto_id
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_state(request):
    data = request.data
    today = datetime.datetime.now()
    serialized = StateSerializer(data=request.data)
    if serialized.is_valid():

        Country_id = serialized.data['Country']
        Name = serialized.data['Name']
        State_Type = serialized.data['State_Type']
        country = Country.objects.get(pk=Country_id)

        is_nameExist = False
        StateNameLow = Name.lower()
        state = State.objects.all()

        for state in state:
            stateName = state.Name.lower()
            if StateNameLow == stateName:
                is_nameExist = True

        if not is_nameExist:
            State.objects.create(
                Country=country,
                Name=Name,
                State_Type=State_Type,
            )
            data = serialized.data
            response_data = {
                "StatusCode": 6000,
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "State Name Already Exist!!!"
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
def edit_state(request, pk):
    data = request.data
    today = datetime.datetime.now()
    serialized = StateSerializer(data=request.data)
    instance = State.objects.get(pk=pk)
    instanceStatename = instance.Name

    if serialized.is_valid():
        Country_id = serialized.data['Country']
        Name = serialized.data['Name']
        State_Type = serialized.data['State_Type']
        country = Country.objects.get(pk=Country_id)

        is_nameExist = False
        state_ok = False
        StateNameLow = Name.lower()

        state = State.objects.all()

        for state in state:
            stateName = state.Name.lower()
            if StateNameLow == stateName:
                is_nameExist = True

            if instanceStatename.lower() == StateNameLow:
                state_ok = True

        if state_ok:

            instance.Country = country
            instance.Name = Name
            instance.State_Type = State_Type
            instance.save()

            data = serialized.data
            response_data = {
                "StatusCode": 6000,
                "data": data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "State Name Already exist"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Country = country
                instance.Name = Name
                instance.State_Type = State_Type
                instance.save()

                data = serialized.data
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


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def states(request):
    data = request.data
    # serialized = ListSerializer(data=request.data)
    if State.objects.all().exists():
        instances = State.objects.all()
        serialized = StateRestSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "States Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def country_state(request, pk):
    data = request.data
    # serialized = ListSerializer(data=request.data)
    if State.objects.all().exists():
        country = Country.objects.get(pk=pk)
        instances = State.objects.filter(Country=country)
        serialized = StateRestSerializer(instances, many=True)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "States Not Found"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def state(request, pk):
    instance = None
    if State.objects.filter(pk=pk).exists():
        instance = State.objects.get(pk=pk)
    if instance:
        serialized = StateRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "State Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_state(request, pk):
    data = request.data
    today = datetime.datetime.now()
    instance = None
    if State.objects.filter(pk=pk).exists():
        instance = State.objects.get(pk=pk)
    if instance:
        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "message": "State Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "State Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
