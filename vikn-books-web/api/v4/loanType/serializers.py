from rest_framework import serializers
from brands.models import LoanType


class LoanTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanType
        fields = ('id','BranchID','Name','Interest')


class LoanTypeRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanType
        fields = ('id','LoanTypeID','BranchID','Name','Interest','CreatedUserID','CreatedDate','UpdatedDate','Action')


