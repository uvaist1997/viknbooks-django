from rest_framework import serializers
from brands.models import LoyaltyProgram,LoyaltyPoint


class LoyaltyProgramSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoyaltyProgram
        fields = ('id','BranchID','Name','ProductType','Calculate_with','FromDate','ToDate','NoOFDayExpPoint','CardTypeID','MinimumSalePrice','Amount','Amount_Point','Percentage','product','ProductCategoryIDs','ProductGroupIDs','is_offer','is_Return_MinimumSalePrice')


class LoyaltyProgramRestSerializer(serializers.ModelSerializer):
    ProductName = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()


    class Meta:
        model = LoyaltyProgram
        fields = ('id','LoyaltyProgramID','CardTypeName','ProductType','Calculate_with','ProductName','BranchID','Name','FromDate','ToDate','NoOFDayExpPoint','CardTypeID','MinimumSalePrice','Amount','Amount_Point','Percentage','product','ProductCategoryIDs','ProductGroupIDs','is_offer','is_Return_MinimumSalePrice','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_ProductName(self, instances):
        name = ""
        if instances.product:
            name = instances.product.ProductName
        return name

    def get_CardTypeName(self, instances):
        CardTypeName = ""
        if instances.CardTypeID:
            CardTypeName = instances.CardTypeID.Name
        return CardTypeName


class LoyaltyPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoyaltyPoint
        fields = ('id','BranchID','is_Radeem','Radeemed_Point','LoyaltyPointID','VoucherType','VoucherMasterID','LoyaltyProgramID','Point','Value','ExpiryDate','LoyaltyCustomerID')
