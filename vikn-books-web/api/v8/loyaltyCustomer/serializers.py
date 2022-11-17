from rest_framework import serializers
from brands.models import LoyaltyCustomer


class LoyaltyCustomerSerializer(serializers.ModelSerializer):
    # CardTypeName = serializers.SerializerMethodField() 

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','BranchID','MobileNo','FirstName','LastName','Address1','Address2','AccountLedgerID','CardNumber','CardTypeID','CardStatusID')


    # def get_CardTypeName(self, instances):
    #     name = instances.CardTypeID.Name
    #     return str(name)

class LoyaltyCustomerRestSerializer(serializers.ModelSerializer):
    CardTypeName = serializers.SerializerMethodField() 

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','LoyaltyCustomerID','BranchID','MobileNo','FirstName','LastName','Address1','Address2','AccountLedgerID','CardNumber','CardTypeID','CardTypeName','CardStatusID','CurrentPoint','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_CardTypeName(self, instances):
        if instances.CardTypeID:
            name = instances.CardTypeID.Name
        else:
            name = ""
        return str(name)