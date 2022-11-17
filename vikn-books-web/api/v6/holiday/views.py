from brands.models import Holiday, Holiday_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.holiday.serializers import HolidaySerializer, HolidayRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.holiday.functions import generate_serializer_errors
from rest_framework import status
from api.v6.holiday.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_holiday(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = HolidaySerializer(data=request.data)
    print(request.data['Date'],
          "sssssssssssssssssssssssssss", request.data['Name'])
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        Name = serialized.data['Name']
        Description = serialized.data['Description']

        Full_day = serialized.data['Full_day']
        FromTime = serialized.data['FromTime']
        ToTime = serialized.data['ToTime']

        is_RecurringHoliday = serialized.data['is_RecurringHoliday']
        HolidayType = serialized.data['HolidayType']

        is_Monday = serialized.data['is_Monday']
        is_Tuesday = serialized.data['is_Tuesday']
        is_Wednesday = serialized.data['is_Wednesday']
        is_Thursday = serialized.data['is_Thursday']
        is_Friday = serialized.data['is_Friday']
        is_Saturday = serialized.data['is_Saturday']
        is_Sunday = serialized.data['is_Sunday']

        Monthly_On = serialized.data['Monthly_On']
        Monthly_day = serialized.data['Monthly_day']
        Monthly_week = serialized.data['Monthly_week']
        Monthly_Weekday = serialized.data['Monthly_Weekday']
        Annually_On = serialized.data['Annually_On']
        Annually_month = serialized.data['Annually_month']

        Annually_day = serialized.data['Annually_day']
        Annually_week = serialized.data['Annually_week']
        Annually_Weekday = serialized.data['Annually_Weekday']
        Annually_Weekmonth = serialized.data['Annually_Weekmonth']
        # Date = request.data['Date']
        try:
            Date = request.data['Date']
            Date_str = str(Date) + ' 08:15:27.243860'
            Date = datetime.datetime.strptime(Date_str, '%Y-%m-%d %H:%M:%S.%f')
            print(Date, "try")
        except:
            Date = None
            print(Date, "except")

        try:
            Annual_FromDate = request.data['Annual_FromDate']
            Annual_FromDate_str = str(Annual_FromDate) + ' 08:15:27.243860'
            Annual_FromDate = datetime.datetime.strptime(
                Annual_FromDate_str, '%Y-%m-%d %H:%M:%S.%f')
            print(Annual_FromDate, "tryAnnual_FromDate")
        except:
            print(Annual_FromDate, "exceptAnnual_FromDate")
            Annual_FromDate = None
        try:
            Annual_ToDate = request.data['Annual_ToDate']
            Annual_ToDate_str = str(Annual_ToDate) + ' 08:15:27.243860'
            Annual_ToDate = datetime.datetime.strptime(
                Annual_ToDate_str, '%Y-%m-%d %H:%M:%S.%f')
            print(Annual_ToDate, "tryAnnual_ToDate")
        except:
            print(Annual_ToDate, "exceptAnnual_ToDate")
            Annual_ToDate = None

        Action = 'A'

        HolidayID = get_auto_id(Holiday, BranchID, CompanyID)
        is_nameExist = False
        HolidayNameLow = Name.lower()
        holidays = Holiday.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for holiday in holidays:
            holiday_name = holiday.Name
            H_Name = holiday_name.lower()
            if HolidayNameLow == H_Name:
                is_nameExist = True

        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            Holiday.objects.create(
                HolidayID=HolidayID,
                BranchID=BranchID,
                Name=Name,

                Description=Description,
                Date=Date,
                Full_day=Full_day,
                FromTime=FromTime,
                ToTime=ToTime,

                is_RecurringHoliday=is_RecurringHoliday,
                HolidayType=HolidayType,

                is_Monday=is_Monday,
                is_Tuesday=is_Tuesday,
                is_Wednesday=is_Wednesday,
                is_Thursday=is_Thursday,
                is_Friday=is_Friday,
                is_Saturday=is_Saturday,
                is_Sunday=is_Sunday,

                Monthly_On=Monthly_On,

                Monthly_day=Monthly_day,
                Monthly_week=Monthly_week,
                Monthly_Weekday=Monthly_Weekday,
                Annually_On=Annually_On,
                Annually_month=Annually_month,

                Annually_day=Annually_day,
                Annually_week=Annually_week,
                Annually_Weekday=Annually_Weekday,
                Annually_Weekmonth=Annually_Weekmonth,
                Annual_FromDate=Annual_FromDate,

                Annual_ToDate=Annual_ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            Holiday_Log.objects.create(
                BranchID=BranchID,
                TransactionID=HolidayID,
                Name=Name,

                Description=Description,
                Date=Date,
                Full_day=Full_day,
                FromTime=FromTime,
                ToTime=ToTime,

                is_RecurringHoliday=is_RecurringHoliday,
                HolidayType=HolidayType,

                is_Monday=is_Monday,
                is_Tuesday=is_Tuesday,
                is_Wednesday=is_Wednesday,
                is_Thursday=is_Thursday,
                is_Friday=is_Friday,
                is_Saturday=is_Saturday,
                is_Sunday=is_Sunday,

                Monthly_On=Monthly_On,
                Monthly_day=Monthly_day,
                Monthly_week=Monthly_week,
                Monthly_Weekday=Monthly_Weekday,
                Annually_On=Annually_On,
                Annually_month=Annually_month,

                Annually_day=Annually_day,
                Annually_week=Annually_week,
                Annually_Weekday=Annually_Weekday,
                Annually_Weekmonth=Annually_Weekmonth,
                Annual_FromDate=Annual_FromDate,

                Annual_ToDate=Annual_ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"HolidayID": HolidayID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Holiday Name Already Exist!!!"
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
def edit_holiday(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = HolidaySerializer(data=request.data)
    instance = Holiday.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    HolidayID = instance.HolidayID
    instanceHolidayname = instance.Name
    if serialized.is_valid():
        Name = serialized.data['Name']

        Description = serialized.data['Description']
        Full_day = serialized.data['Full_day']
        FromTime = serialized.data['FromTime']
        ToTime = serialized.data['ToTime']

        is_RecurringHoliday = serialized.data['is_RecurringHoliday']
        HolidayType = serialized.data['HolidayType']
        is_Monday = serialized.data['is_Monday']
        is_Tuesday = serialized.data['is_Tuesday']
        is_Wednesday = serialized.data['is_Wednesday']

        is_Thursday = serialized.data['is_Thursday']
        is_Friday = serialized.data['is_Friday']
        is_Saturday = serialized.data['is_Saturday']
        is_Sunday = serialized.data['is_Sunday']

        Monthly_On = serialized.data['Monthly_On']
        # Monthly
        Monthly_day = serialized.data['Monthly_day']
        Monthly_week = serialized.data['Monthly_week']
        Monthly_Weekday = serialized.data['Monthly_Weekday']

        Annually_On = serialized.data['Annually_On']
        # Annually
        Annually_month = serialized.data['Annually_month']
        Annually_day = serialized.data['Annually_day']

        Annually_week = serialized.data['Annually_week']
        Annually_Weekday = serialized.data['Annually_Weekday']
        Annually_Weekmonth = serialized.data['Annually_Weekmonth']

        try:
            Date = request.data['Date']
            Date_str = str(Date) + ' 08:15:27.243860'
            Date = datetime.datetime.strptime(Date_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            Date = instance.Date

        try:
            Annual_FromDate = request.data['Annual_FromDate']
            Annual_FromDate_str = str(Annual_FromDate) + ' 08:15:27.243860'
            Annual_FromDate = datetime.datetime.strptime(
                Annual_FromDate_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            Annual_FromDate = instance.Annual_FromDate
        try:
            Annual_ToDate = request.data['Annual_ToDate']
            Annual_ToDate_str = str(Annual_ToDate) + ' 08:15:27.243860'
            Annual_ToDate = datetime.datetime.strptime(
                Annual_ToDate_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            Annual_ToDate = instance.Annual_ToDate

        if Annually_On == "Annually_On_day":
            print('Annually_On_day')
            Annual_FromDate = None
            Annual_ToDate = None
            Annually_week = None
            Annually_Weekday = None
            Annually_Weekmonth = None
        elif Annually_On == "Annually_On_week":
            print('Annually_On_week')
            Annual_FromDate = None
            Annual_ToDate = None

            Annually_month = None
            Annually_day = None

        elif Annually_On == "Annually_On_year":
            Annually_month = None
            Annually_day = None

            Annually_week = None
            Annually_Weekday = None
            Annually_Weekmonth = None

        Action = 'M'
        is_nameExist = False
        holiday_ok = False

        HolidayNameLow = Name.lower()

        holidays = Holiday.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for holiday in holidays:
            holiday_name = holiday.Name

            holidayName = holiday_name.lower()

            if HolidayNameLow == holidayName:
                is_nameExist = True

            if instanceHolidayname.lower() == HolidayNameLow:

                holiday_ok = True

        if holiday_ok:

            instance.Name = Name

            instance.Description = Description

            instance.Date = Date
            instance.Full_day = Full_day
            instance.FromTime = FromTime
            instance.ToTime = ToTime
            instance.is_RecurringHoliday = is_RecurringHoliday
            instance.HolidayType = HolidayType
            instance.is_Monday = is_Monday
            instance.is_Tuesday = is_Tuesday
            instance.is_Wednesday = is_Wednesday
            instance.is_Thursday = is_Thursday
            instance.is_Friday = is_Friday
            instance.is_Saturday = is_Saturday
            instance.is_Sunday = is_Sunday
            instance.Monthly_On = Monthly_On
            instance.Monthly_day = Monthly_day
            instance.Monthly_week = Monthly_week
            instance.Monthly_Weekday = Monthly_Weekday
            instance.Annually_On = Annually_On
            instance.Annually_month = Annually_month
            instance.Annually_day = Annually_day
            instance.Annually_week = Annually_week
            instance.Annually_Weekday = Annually_Weekday
            instance.Annually_Weekmonth = Annually_Weekmonth
            instance.Annual_FromDate = Annual_FromDate
            instance.Annual_ToDate = Annual_ToDate

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Holiday_Log.objects.create(
                BranchID=BranchID,
                TransactionID=HolidayID,
                Name=Name,

                Description=Description,
                Date=Date,
                Full_day=Full_day,
                FromTime=FromTime,
                ToTime=ToTime,

                is_RecurringHoliday=is_RecurringHoliday,
                HolidayType=HolidayType,

                is_Monday=is_Monday,
                is_Tuesday=is_Tuesday,
                is_Wednesday=is_Wednesday,
                is_Thursday=is_Thursday,
                is_Friday=is_Friday,
                is_Saturday=is_Saturday,
                is_Sunday=is_Sunday,

                Monthly_On=Monthly_On,
                Monthly_day=Monthly_day,
                Monthly_week=Monthly_week,
                Monthly_Weekday=Monthly_Weekday,
                Annually_On=Annually_On,
                Annually_month=Annually_month,

                Annually_day=Annually_day,
                Annually_week=Annually_week,
                Annually_Weekday=Annually_Weekday,
                Annually_Weekmonth=Annually_Weekmonth,
                Annual_FromDate=Annual_FromDate,

                Annual_ToDate=Annual_ToDate,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"HolidayID": HolidayID}
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
                    "message": "Holiday Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name

                instance.Description = Description
                instance.Date = Date
                instance.Full_day = Full_day
                instance.FromTime = FromTime
                instance.ToTime = ToTime
                instance.is_RecurringHoliday = is_RecurringHoliday
                instance.HolidayType = HolidayType
                instance.is_Monday = is_Monday
                instance.is_Tuesday = is_Tuesday
                instance.is_Wednesday = is_Wednesday
                instance.is_Thursday = is_Thursday
                instance.is_Friday = is_Friday
                instance.is_Saturday = is_Saturday
                instance.is_Sunday = is_Sunday
                instance.Monthly_On = Monthly_On
                instance.Monthly_day = Monthly_day
                instance.Monthly_week = Monthly_week
                instance.Monthly_Weekday = Monthly_Weekday
                instance.Annually_On = Annually_On
                instance.Annually_month = Annually_month
                instance.Annually_day = Annually_day
                instance.Annually_week = Annually_week
                instance.Annually_Weekday = Annually_Weekday
                instance.Annually_Weekmonth = Annually_Weekmonth
                instance.Annual_FromDate = Annual_FromDate
                instance.Annual_ToDate = Annual_ToDate

                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                Holiday_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=HolidayID,
                    HolidayName=HolidayName,

                    Description=Description,
                    Date=Date,
                    Full_day=Full_day,
                    FromTime=FromTime,
                    ToTime=ToTime,

                    is_RecurringHoliday=is_RecurringHoliday,
                    HolidayType=HolidayType,

                    is_Monday=is_Monday,
                    is_Tuesday=is_Tuesday,
                    is_Wednesday=is_Wednesday,
                    is_Thursday=is_Thursday,
                    is_Friday=is_Friday,
                    is_Saturday=is_Saturday,
                    is_Sunday=is_Sunday,

                    Monthly_On=Monthly_On,
                    Monthly_day=Monthly_day,
                    Monthly_week=Monthly_week,
                    Monthly_Weekday=Monthly_Weekday,
                    Annually_On=Annually_On,
                    Annually_month=Annually_month,

                    Annually_day=Annually_day,
                    Annually_week=Annually_week,
                    Annually_Weekday=Annually_Weekday,
                    Annually_Weekmonth=Annually_Weekmonth,
                    Annual_FromDate=Annual_FromDate,
                    Annual_ToDate=Annual_ToDate,


                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"HolidayID": HolidayID}
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
def holidays(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Holiday.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Holiday.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = HolidayRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Holiday Not Found in this BranchID!"
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
def holiday(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Holiday.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Holiday.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = HolidayRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Holiday Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_holiday(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Holiday.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Holiday.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        HolidayID = instance.HolidayID
        Name = instance.Name

        Description = instance.Description
        Date = instance.Date
        Full_day = instance.Full_day
        FromTime = instance.FromTime
        ToTime = instance.ToTime
        is_RecurringHoliday = instance.is_RecurringHoliday
        HolidayType = instance.HolidayType
        is_Monday = instance.is_Monday
        is_Tuesday = instance.is_Tuesday
        is_Wednesday = instance.is_Wednesday
        is_Thursday = instance.is_Thursday
        is_Friday = instance.is_Friday
        is_Saturday = instance.is_Saturday
        is_Sunday = instance.is_Sunday
        Monthly_On = instance.Monthly_On
        Monthly_day = instance.Monthly_day
        Monthly_week = instance.Monthly_week
        Monthly_Weekday = instance.Monthly_Weekday
        Annually_On = instance.Annually_On
        Annually_month = instance.Annually_month
        Annually_day = instance.Annually_day
        Annually_week = instance.Annually_week
        Annually_Weekday = instance.Annually_Weekday
        Annually_Weekmonth = instance.Annually_Weekmonth
        Annual_FromDate = instance.Annual_FromDate
        Annual_ToDate = instance.Annual_ToDate

        Action = "D"

        instance.delete()

        Holiday_Log.objects.create(
            BranchID=BranchID,
            TransactionID=HolidayID,
            Name=Name,

            Description=Description,
            Date=Date,
            Full_day=Full_day,
            FromTime=FromTime,
            ToTime=ToTime,

            is_RecurringHoliday=is_RecurringHoliday,
            HolidayType=HolidayType,

            is_Monday=is_Monday,
            is_Tuesday=is_Tuesday,
            is_Wednesday=is_Wednesday,
            is_Thursday=is_Thursday,
            is_Friday=is_Friday,
            is_Saturday=is_Saturday,
            is_Sunday=is_Sunday,

            Monthly_On=Monthly_On,
            Monthly_day=Monthly_day,
            Monthly_week=Monthly_week,
            Monthly_Weekday=Monthly_Weekday,
            Annually_On=Annually_On,
            Annually_month=Annually_month,

            Annually_day=Annually_day,
            Annually_week=Annually_week,
            Annually_Weekday=Annually_Weekday,
            Annually_Weekmonth=Annually_Weekmonth,
            Annual_FromDate=Annual_FromDate,
            Annual_ToDate=Annual_ToDate,

            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Holiday Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Holiday Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
