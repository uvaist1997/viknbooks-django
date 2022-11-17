from rest_framework import serializers
from brands.models import SalaryPeriod


class SalaryPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryPeriod
        fields = ('id','BranchID','Name','Note','Year')


class SalaryPeriodRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryPeriod
        fields = ('id','SalaryPeriodID','BranchID','Name','Note','Year','FromDate','ToDate','CreatedUserID','CreatedDate','UpdatedDate','Action')


