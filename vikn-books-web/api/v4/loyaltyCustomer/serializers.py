from rest_framework import serializers
from brands.models import LoyaltyCustomer


class LoyaltyCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','BranchID','MobileNo','FirstName','LastName','Address1','Address2','AccountLedgerID','CardNumber','CardTypeID','CardStatusID')


class LoyaltyCustomerRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','LoyaltyCustomerID','BranchID','MobileNo','FirstName','LastName','Address1','Address2','AccountLedgerID','CardNumber','CardTypeID','CardStatusID','CurrentPoint','CreatedUserID','CreatedDate','UpdatedDate','Action')


