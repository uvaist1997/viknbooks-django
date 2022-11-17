from rest_framework import serializers
from brands.models import FinancialYear


class FinancialYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = FinancialYear
        fields = ('CompanyID','id','FromDate','ToDate','Notes','IsClosed','CreatedUserID')

