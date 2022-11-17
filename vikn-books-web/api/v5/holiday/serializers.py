from rest_framework import serializers
from brands.models import Holiday


class HolidaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = ('id','BranchID','Name','Description','Full_day','FromTime','ToTime','is_RecurringHoliday','HolidayType','is_Monday','is_Tuesday','is_Wednesday','is_Thursday','is_Friday','is_Saturday','is_Sunday','Monthly_On','Monthly_day','Monthly_week','Monthly_Weekday','Annually_On','Annually_month','Annually_day','Annually_week','Annually_Weekday','Annually_Weekmonth')


class HolidayRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Holiday
        fields = ('id','HolidayID','BranchID','Name','Description','Date','Full_day','FromTime','ToTime','is_RecurringHoliday','HolidayType','is_Monday','is_Tuesday','is_Wednesday','is_Thursday','is_Friday','is_Saturday','is_Sunday','Monthly_On','Monthly_day','Monthly_week','Monthly_Weekday','Annually_On','Annually_month','Annually_day','Annually_week','Annually_Weekday','Annually_Weekmonth','Annual_FromDate','Annual_ToDate','CreatedUserID','CreatedDate','UpdatedDate','Action')


