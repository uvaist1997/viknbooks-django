import datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.countries.functions import generate_serializer_errors, get_auto_id
from api.v10.countries.serializers import (
    CountryRestSerializer,
    CountrySerializer,
    ListSerializer,
)
from brands.models import CompanySettings, Country, Product
from main.functions import get_company


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_country(request):
    data = request.data
    Flag = data["Flag"]
    today = datetime.datetime.now()
    serialized = CountrySerializer(data=request.data)
    if serialized.is_valid():

        CountryCode = serialized.data["CountryCode"]
        Country_Name = serialized.data["Country_Name"]
        Currency_Name = serialized.data["Currency_Name"]
        Change = serialized.data["Change"]
        Symbol = serialized.data["Symbol"]
        FractionalUnits = serialized.data["FractionalUnits"]
        CurrencySymbolUnicode = serialized.data["CurrencySymbolUnicode"]
        ISD_Code = serialized.data["ISD_Code"]
        Tax_Type = serialized.data["Tax_Type"]

        is_nameExist = False
        CountryNameLow = Country_Name.lower()
        countries = Country.objects.all()

        for country in countries:
            countryName = country.Country_Name.lower()
            if CountryNameLow == countryName:
                is_nameExist = True

        if not is_nameExist:

            Country.objects.create(
                CountryCode=CountryCode,
                Country_Name=Country_Name,
                Currency_Name=Currency_Name,
                Change=Change,
                Symbol=Symbol,
                FractionalUnits=FractionalUnits,
                CurrencySymbolUnicode=CurrencySymbolUnicode,
                ISD_Code=ISD_Code,
                Flag=Flag,
                Tax_Type=Tax_Type,
            )
            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Country Name Already Exist!!!",
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
def edit_country(request, pk):
    data = request.data
    Flag = data["Flag"]
    today = datetime.datetime.now()
    serialized = CountrySerializer(data=request.data)
    instance = Country.objects.get(pk=pk)
    instanceCountryname = instance.Country_Name

    if serialized.is_valid():
        CountryCode = serialized.data["CountryCode"]
        Country_Name = serialized.data["Country_Name"]
        Currency_Name = serialized.data["Currency_Name"]
        Change = serialized.data["Change"]
        Symbol = serialized.data["Symbol"]
        FractionalUnits = serialized.data["FractionalUnits"]
        CurrencySymbolUnicode = serialized.data["CurrencySymbolUnicode"]
        ISD_Code = serialized.data["ISD_Code"]
        Tax_Type = serialized.data["Tax_Type"]

        is_nameExist = False
        country_ok = False
        CountryNameLow = Country_Name.lower()

        countries = Country.objects.all()

        for country in countries:
            countryName = country.Country_Name.lower()
            if CountryNameLow == countryName:
                is_nameExist = True

            if instanceCountryname.lower() == CountryNameLow:
                country_ok = True

        if country_ok:

            instance.CountryCode = CountryCode
            instance.Country_Name = Country_Name
            instance.Currency_Name = Currency_Name
            instance.Change = Change
            instance.Symbol = Symbol
            instance.FractionalUnits = FractionalUnits
            instance.CurrencySymbolUnicode = CurrencySymbolUnicode
            instance.ISD_Code = ISD_Code
            instance.Tax_Type = Tax_Type
            instance.Flag = Flag
            instance.save()

            data = serialized.data
            response_data = {"StatusCode": 6000, "data": data}
            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Country Name Already exist",
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.CountryCode = CountryCode
                instance.Country_Name = Country_Name
                instance.Currency_Name = Currency_Name
                instance.Change = Change
                instance.Symbol = Symbol
                instance.FractionalUnits = FractionalUnits
                instance.CurrencySymbolUnicode = CurrencySymbolUnicode
                instance.ISD_Code = ISD_Code
                instance.Tax_Type = Tax_Type
                instance.Flag = Flag
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
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def countries(request):
    data = request.data
    serialized = ListSerializer(data=request.data)
    if Country.objects.all().exists():
        instances = Country.objects.all()
        serialized = CountryRestSerializer(instances, many=True)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "Countrys Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def country_tax_type(request, pk):
    data = request.data
    # serialized = ListSerializer(data=request.data)
    if Country.objects.all().exists():
        instance = Country.objects.get(pk=pk)
        # instances = State.objects.filter(Country=country)
        serialized = CountryRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {"StatusCode": 6001, "message": "States Not Found"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def country(request, pk):
    data = request.data
    # CompanyID = data['CompanyID']
    # CompanyID = get_company(CompanyID)
    # CreatedUserID = data['CreatedUserID']

    instance = None
    if Country.objects.filter(pk=pk).exists():
        instance = Country.objects.get(pk=pk)
    if instance:
        serialized = CountryRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        response_data = {"StatusCode": 6001, "message": "Country Not Fount!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_country(request, pk):
    data = request.data
    today = datetime.datetime.now()
    instance = None
    if Country.objects.filter(pk=pk).exists():
        instance = Country.objects.get(pk=pk)
        if not CompanySettings.objects.filter(Country=instance).exists():
            instance.delete()
            response_data = {
                "StatusCode": 6000,
                "message": "Country Deleted Successfully!",
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Country Already Using!can't delete",
            }
    else:
        response_data = {"StatusCode": 6001, "message": "Country Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)
