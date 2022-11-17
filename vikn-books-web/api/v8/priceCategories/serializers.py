from rest_framework import serializers
from brands.models import PriceCategory


class PriceCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceCategory
        fields = ('id','BranchID','PriceCategoryName','ColumnName','IsActive','Notes','CreatedUserID','CreatedDate')


class PriceCategoryRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceCategory
        fields = ('id','PriceCategoryID','BranchID','PriceCategoryName','ColumnName','IsActive','Notes','CreatedUserID','CreatedDate','Action')
