from rest_framework import serializers
from brands.models import SalaryComponent


class SalaryComponentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryComponent
        fields = ('id','BranchID','Name','Description','ComponentType','ExpressionType','ExpressionValue','Status')


class SalaryComponentRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryComponent
        fields = ('id','SalaryComponentID','BranchID','Name','Description','ComponentType','ExpressionType','ExpressionValue','Status','CreatedUserID','CreatedDate','UpdatedDate','Action')


