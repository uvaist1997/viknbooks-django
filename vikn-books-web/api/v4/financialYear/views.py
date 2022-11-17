from brands.models import Brand, Brand_Log, Product
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.financialYear.serializers import FinancialYearSerializer
from api.v4.brands.functions import generate_serializer_errors
from administrations.functions import get_auto_id_user_type, get_auto_id_financial_year
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from api.v4.brands.functions import get_auto_id
from brands import models as administrations_models
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_financial_year(request):
    data = request.data
    CompanyID = data['CompanyID']

    today = datetime.datetime.now()
    serialized = FinancialYearSerializer(data=request.data)
    if not administrations_models.FinancialYear.objects.filter(IsClosed=False, CompanyID=CompanyID).exists():
        if serialized.is_valid():
            CreatedUserID = serialized.data['CreatedUserID']
            # CompanyID = serialized.data['CompanyID']
            CompanyID = get_company(CompanyID)
            FromDate = serialized.data['FromDate']
            FromDate = datetime.datetime.strptime(FromDate, '%Y-%m-%d')
            ToDate = serialized.data['ToDate']
            ToDate = datetime.datetime.strptime(ToDate, '%Y-%m-%d')
            Notes = serialized.data['Notes']
            print(FromDate)
            print("checking data")
            print(ToDate)
            days = ToDate - FromDate
            days = str(days).split(' ')

            test = administrations_models.FinancialYear.objects.filter(
                IsClosed=True, CompanyID=CompanyID)
            date_arr = []
            for i in test:
                date_form = i.FromDate
                date_to = i.ToDate
                # database date filter
                start = datetime.datetime.strptime(str(date_form), "%Y-%m-%d")
                end = datetime.datetime.strptime(str(date_to), "%Y-%m-%d")
                date_array = \
                    (start + datetime.timedelta(days=x)
                     for x in range(0, (end-start).days))

                for date_object in date_array:
                    date = date_object.strftime("%Y-%m-%d")
                    date_arr.append(date)
            if str(FromDate) in date_arr or str(ToDate) in date_arr:
                response_data = {
                    "StatusCode": 6001,
                    "message": "This Financial Year is Alredy Exists"
                }
            else:
                if days[0] == '364' or days[0] == '365':
                    auto_id = get_auto_id_financial_year(
                        administrations_models.FinancialYear, CompanyID)
                    financial_year_save = administrations_models.FinancialYear.objects.create(
                        Action='A',
                        CreatedUserID=request.user.id,
                        FinancialYearID=auto_id,
                        FromDate=FromDate,
                        ToDate=ToDate,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Notes=Notes,
                        IsClosed=False,
                        CompanyID=CompanyID,
                    )

                    administrations_models.FinancialYear_Log.objects.create(
                        TransactionID=financial_year_save.FinancialYearID,
                        Action=financial_year_save.Action,
                        FromDate=FromDate,
                        ToDate=ToDate,
                        Notes=Notes,
                        CreatedDate=financial_year_save.CreatedDate,
                        UpdatedDate=financial_year_save.UpdatedDate,
                        CreatedUserID=financial_year_save.CreatedUserID,
                        IsClosed=False,
                        CompanyID=CompanyID,
                    )
                    response_data = {
                        "StatusCode": 6000,
                        "message": 'Successfully Created'
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Financial Year Must Have 1 Year"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": str('Current financial year is not closed')
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_financial_year(request, pk):

    data = request.data
    print(data)
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    today = datetime.datetime.now()
    serialized = FinancialYearSerializer(data=request.data)
    instance = administrations_models.FinancialYear.objects.get(
        pk=pk, CompanyID=CompanyID)

    FinancialYearID = instance.FinancialYearID
    CreatedDate = instance.CreatedDate
    UpdatedDate = instance.UpdatedDate
    CreatedUserID = instance.CreatedUserID

    if serialized.is_valid():
        FromDate = serialized.data['FromDate']
        FromDate = datetime.datetime.strptime(FromDate, '%Y-%m-%d')
        ToDate = serialized.data['ToDate']
        ToDate = datetime.datetime.strptime(ToDate, '%Y-%m-%d')
        Notes = serialized.data['Notes']
        IsClosed = serialized.data['IsClosed']
        # if IsClosed == False:
        #     IsClosed = 'false'
        administrations_models.FinancialYear.objects.filter(pk=pk, CompanyID=CompanyID).update(
            Action='M',
            FromDate=FromDate,
            ToDate=ToDate,
            IsClosed=IsClosed,
            Notes=Notes,
            CreatedDate=CreatedDate,
            UpdatedDate=UpdatedDate,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        administrations_models.FinancialYear_Log.objects.create(
            TransactionID=FinancialYearID,
            Action='M',
            FromDate=FromDate,
            ToDate=ToDate,
            IsClosed=IsClosed,
            Notes=Notes,
            CreatedDate=CreatedDate,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def financial_years(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    instances = administrations_models.FinancialYear.objects.filter(
        CompanyID=CompanyID)
    closed_instances = administrations_models.FinancialYear.objects.filter(
        CompanyID=CompanyID, IsClosed=True).last()
    serialized = FinancialYearSerializer(instances, many=True)
    closed_serialized = FinancialYearSerializer(closed_instances)
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data,
        "closed_data": closed_serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def financial_year(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if administrations_models.FinancialYear.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = administrations_models.FinancialYear.objects.get(
            pk=pk, CompanyID=CompanyID)
    if instance:
        serialized = FinancialYearSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Financial Year Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_financial_year(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    today = today = datetime.datetime.now()
    instance = administrations_models.FinancialYear.objects.get(
        pk=pk, CompanyID=CompanyID)

    if pk == "1" and pk == "2":
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "can't delete this Financial Year"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        administrations_models.FinancialYear_Log.objects.create(
            TransactionID=instance.FinancialYearID,
            Action="D",
            FromDate=instance.FromDate,
            ToDate=instance.ToDate,
            IsClosed=instance.IsClosed,
            Notes=instance.Notes,
            CreatedDate=instance.CreatedDate,
            UpdatedDate=today,
            CreatedUserID=instance.CreatedUserID,
            CompanyID=CompanyID,
        )
        instance.delete()
        response_data = {
            "StatusCode": 6000,
            "title": 'Success',
            "message": "Successfully Deleted"
        }

        return Response(response_data, status=status.HTTP_200_OK)
