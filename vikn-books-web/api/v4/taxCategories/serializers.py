from rest_framework import serializers
from brands.models import TaxCategory, TaxType


class TaxCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxCategory
        fields = ('id','BranchID','TaxName','TaxType','PurchaseTax','SalesTax','Inclusive','CreatedUserID')


class TaxCategoryRestSerializer(serializers.ModelSerializer):

    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    TaxType = serializers.SerializerMethodField()
    TaxTypeID = serializers.SerializerMethodField()

    class Meta:
        model = TaxCategory
        fields = ('id','TaxID','BranchID','TaxName','TaxType','TaxTypeID','PurchaseTax','SalesTax','Inclusive','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_PurchaseTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        PurchaseTax = instances.PurchaseTax

        PurchaseTax = round(PurchaseTax,PriceRounding)

        return str(PurchaseTax)

    def get_SalesTax(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        SalesTax = instances.SalesTax

        SalesTax = round(SalesTax,PriceRounding)

        return str(SalesTax)


    def get_TaxTypeID(self, instance):
     
        CompanyID = self.context.get("CompanyID")

        BranchID = instance.BranchID
        TaxTypeID = instance.TaxType

        return TaxTypeID


    def get_TaxType(self, instance):
     
        CompanyID = self.context.get("CompanyID")

        BranchID = instance.BranchID
        tax = instance.TaxType

        TaxTypeName = ""

        if TaxType.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TaxTypeID=tax).exists():
            type_instance = TaxType.objects.get(CompanyID=CompanyID,BranchID=BranchID,TaxTypeID=tax)

            TaxTypeName = type_instance.TaxTypeName

        return TaxTypeName
      

class ListSerializerTaxType(serializers.Serializer):

    BranchID = serializers.IntegerField()
    TaxType = serializers.CharField()


class TaxTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxCategory
        fields = ('id','TaxID','TaxName','TaxType')



class ListTaxTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaxType
        fields = ('id','TaxTypeID','BranchID','TaxTypeName','Active')