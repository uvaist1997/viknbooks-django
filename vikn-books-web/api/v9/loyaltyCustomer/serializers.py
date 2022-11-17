from rest_framework import serializers
from brands.models import LoyaltyCustomer


class LoyaltyCustomerSerializer(serializers.ModelSerializer):
    # CardTypeName = serializers.SerializerMethodField() 

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','BranchID','MobileNo','FirstName','LastName','Address1','Address2','AccountLedgerID','CardNumber')


    # def get_CardTypeName(self, instances):
    #     name = instances.CardTypeID.Name
    #     return str(name)

class LoyaltyCustomerRestSerializer(serializers.ModelSerializer):
    CardTypeName = serializers.SerializerMethodField() 
    CardStatusName = serializers.SerializerMethodField() 
    CustomerName = serializers.SerializerMethodField()
    customerList = serializers.SerializerMethodField()
    namePhone = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyCustomer
        fields = ('id','LoyaltyCustomerID','BranchID','MobileNo','FirstName','LastName','Address1','Address2',
                  'AccountLedgerID','CardNumber','CardTypeID','CardTypeName',
                  'CardStatusID','CurrentPoint','CreatedUserID','CreatedDate',
                  'UpdatedDate','Action',"CardStatusName","CustomerName","customerList","namePhone")


    def get_CardTypeName(self, instances):
        name = ""
        if instances.CardTypeID:
            name = instances.CardTypeID.Name
        return str(name)
    
    def get_namePhone(self, instances):
        name = ""
        if instances.AccountLedgerID:
            LedgerName = instances.AccountLedgerID.LedgerName
            MobileNo = instances.MobileNo
            name = str(MobileNo)+str("-")+str(LedgerName)
            
        return str(name)
    
    
    def get_CardStatusName(self, instances):
        name = ""
        if instances.CardStatusID:
            name = instances.CardStatusID.Name
        return str(name)
    
    def get_CustomerName(self, instances):
        name = ""
        if instances.AccountLedgerID:
            name = instances.AccountLedgerID.LedgerName
        return str(name)
    
    def get_customerList(self, instances):
        customerList = []
        if instances.AccountLedgerID:
            name = instances.AccountLedgerID.LedgerName
            customerList.append({
                "LedgerName": name,
                "LedgerID": instances.AccountLedgerID.LedgerID,
                "id": instances.AccountLedgerID.id,
            })
        return customerList