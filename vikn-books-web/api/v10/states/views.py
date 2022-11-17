import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.states.functions import generate_serializer_errors, get_auto_id
from api.v10.states.serializers import (
    ListSerializer,
    StateRestSerializer,
    StateSerializer,
    UQCSerializer,
)
from brands.models import CompanySettings, Country, Product, State, UQCTable
from main.functions import get_company


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_state(request):
    data = request.data
    today = datetime.datetime.now()
    serialized = StateSerializer(data=request.data)
    if serialized.is_valid():

        Country_id = serialized.data["Country"]
        Name = serialized.data["Name"]
        State_Type = serialized.data["State_Type"]
        try:
            State_Code = serialized.data["State_Code"]
        except:
            State_Code = None

        country = Country.objects.get(pk=Country_id)

        is_nameExist = False
        StateNameLow = Name.lower()
        state = State.objects.all()

        for state in state:
            stateName = state.Name.lower()
            if StateNameLow == stateName:
                is_nameExist = True

        # state_list = [

        #     {"Country_id": Country_id, "Name": "Jammu and Kashmir",
        #         "State_Code": "01", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Himachal Pradesh",
        #         "State_Code": "02", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Punjab",
        #         "State_Code": "03", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Chandigarh",
        #         "State_Code": "04", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Uttarakhand",
        #         "State_Code": "05", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Haryana",
        #         "State_Code": "06", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Delhi",
        #         "State_Code": "07", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Rajasthan",
        #         "State_Code": "08", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Uttar Pradesh",
        #         "State_Code": "09", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Bihar",
        #         "State_Code": "10", "State_Type": ""},

        #     {"Country_id": Country_id, "Name": "Sikkim",
        #         "State_Code": "11", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Arunachal Pradesh",
        #         "State_Code": "12", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Nagaland",
        #         "State_Code": "13", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Manipur",
        #         "State_Code": "14", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Mizoram",
        #         "State_Code": "15", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Tripura",
        #         "State_Code": "16", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Meghalaya",
        #         "State_Code": "17", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Assam",
        #         "State_Code": "18", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "West Bengal",
        #         "State_Code": "19", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Jharkhand",
        #         "State_Code": "20", "State_Type": ""},

        #     {"Country_id": Country_id, "Name": "Orissa",
        #         "State_Code": "21", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Chhattisgarh",
        #         "State_Code": "22", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Madhya Pradesh",
        #         "State_Code": "23", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Gujarat",
        #         "State_Code": "24", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Daman and Diu",
        #         "State_Code": "25", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Dadra & Nagar Haveli",
        #         "State_Code": "26", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Maharashtra",
        #         "State_Code": "27", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Andhra",
        #         "State_Code": "28", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Karnataka",
        #         "State_Code": "29", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Goa",
        #         "State_Code": "30", "State_Type": ""},

        #     {"Country_id": Country_id, "Name": "Lakshadweep",
        #         "State_Code": "31", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Kerala",
        #         "State_Code": "32", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Tamil Nadu",
        #         "State_Code": "33", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Puducherry",
        #         "State_Code": "34", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Andaman and Nicobar Islands",
        #         "State_Code": "35", "State_Type": ""},
        #     {"Country_id": Country_id, "Name": "Telengana",
        #         "State_Code": "36", "State_Type": ""},
        #     {"Country_id": Country_id,
        #         "Name": "Andhra Pradesh(New)", "State_Code": "37", "State_Type": ""},

        # ]

        # for i in state_list:
        #     Country_id = i["Country_id"]
        #     country = Country.objects.get(pk=Country_id)
        #     Name = i["Name"]
        #     State_Code = i["State_Code"]
        #     State_Type = ""
        #     State.objects.create(
        #         Country=country,
        #         Name=Name,
        #         State_Code=State_Code,
        #         State_Type=State_Type,
        #     )

        if not is_nameExist:
            State.objects.create(
                Country=country,
                Name=Name,
                State_Code=State_Code,
                State_Type=State_Type,
            )
            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "State Name Already Exist!!!",
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
def edit_state(request, pk):
    data = request.data
    today = datetime.datetime.now()
    serialized = StateSerializer(data=request.data)
    instance = State.objects.get(pk=pk)
    instanceStatename = instance.Name

    if serialized.is_valid():
        Country_id = serialized.data["Country"]
        Name = serialized.data["Name"]
        State_Type = serialized.data["State_Type"]
        State_Code = serialized.data["State_Code"]
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
            instance.State_Code = State_Code
            instance.save()

            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "State Name Already exist",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Country = country
                instance.Name = Name
                instance.State_Type = State_Type
                instance.State_Code = State_Code

                instance.save()

                data = serialized.data
                response_data = {"StatusCode": 6000, "data": data}

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def states(request):
    data = request.data
    # serialized = ListSerializer(data=request.data)
    if State.objects.all().exists():
        instances = State.objects.all()
        serialized = StateRestSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "States Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def get_state_detail(request):
    data = request.data
    state_code = data["State_Code"]
    print(state_code)
    instance = None
    # serialized = ListSerializer(data=request.data)
    if State.objects.filter(State_Code=state_code).exists():
        instance = State.objects.get(State_Code=state_code)
        serialized = StateRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "States Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def country_state(request, pk):
    data = request.data
    # serialized = ListSerializer(data=request.data)
    if State.objects.all().exists():
        country = Country.objects.get(pk=pk)
        instances = State.objects.filter(Country=country)
        serialized = StateRestSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "States Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def state(request, pk):
    instance = None
    if State.objects.filter(pk=pk).exists():
        instance = State.objects.get(pk=pk)
    if instance:
        serialized = StateRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "State Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_state(request, pk):
    data = request.data
    today = datetime.datetime.now()
    if State.objects.filter(pk=pk).exists():
        instance = State.objects.get(pk=pk)
        if not CompanySettings.objects.filter(State=instance).exists():

            instance.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "State Deleted Successfully!",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "State Already Using!can't delete",
            }

    else:
        response_data = {"StatusCode": 6001, "message": "State Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_UQC(request):
    data = request.data
    today = datetime.datetime.now()
    serialized = UQCSerializer(data=request.data)
    if serialized.is_valid():
        UQC_Name = serialized.data["UQC_Name"]
        is_nameExist = False
        UQCNameLow = UQC_Name.lower()

        UQCs = UQCTable.objects.all()
        for u in UQCs:
            uqc_name = u.UQC_Name.lower()
            if UQCNameLow == uqc_name:
                is_nameExist = True

        if not is_nameExist:
            UQCTable.objects.create(
                UQC_Name=UQC_Name,
            )
            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"StatusCode": 6001, "message": "UQC Already Exist!!!"}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_UQC(request):
    if UQCTable.objects.all().exists():
        instances = UQCTable.objects.all()
        serialized = UQCSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "UQCs Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_UQC(request, pk):
    data = request.data
    today = datetime.datetime.now()
    serialized = UQCSerializer(data=request.data)
    instance = UQCTable.objects.get(pk=pk)
    instanceUQCname = instance.UQC_Name

    if serialized.is_valid():
        UQC_Name = serialized.data["UQC_Name"]

        is_nameExist = False
        uqc_ok = False
        UQCNameLow = UQC_Name.lower()

        UQCs = UQCTable.objects.all()

        for uqc in UQCs:
            uqcName = uqc.UQC_Name.lower()
            if UQCNameLow == uqcName:
                is_nameExist = True

            if instanceUQCname.lower() == UQCNameLow:
                uqc_ok = True

        if uqc_ok:
            instance.UQC_Name = UQC_Name
            instance.save()

            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            if is_nameExist:
                response_data = {
                    "StatusCode": 6001,
                    "message": "UQC Name Already exist",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.UQC_Name = UQC_Name
                instance.save()

                data = serialized.data
                response_data = {"StatusCode": 6000, "data": data}

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def view_UQC(request, pk):
    instance = None
    if UQCTable.objects.filter(pk=pk).exists():
        instance = UQCTable.objects.get(pk=pk)
    if instance:
        serialized = UQCSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "UQC Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_UQC(request, pk):
    data = request.data
    today = datetime.datetime.now()
    if UQCTable.objects.filter(pk=pk).exists():
        instance = UQCTable.objects.get(pk=pk)
        instance.delete()
        response_data = {"StatusCode": 6000, "message": "State Deleted Successfully!"}
    else:
        response_data = {"StatusCode": 6001, "message": "State Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)
