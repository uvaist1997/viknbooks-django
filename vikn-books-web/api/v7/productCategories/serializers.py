from rest_framework import serializers
from brands.models import ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = ('id','BranchID','CategoryName','Notes','CreatedUserID')


class ProductCategoryRestSerializer(serializers.ModelSerializer):

    ProductCategoryName = serializers.SerializerMethodField()
    class Meta:
        model = ProductCategory
        fields = ('id','ProductCategoryID','BranchID','CategoryName','ProductCategoryName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_ProductCategoryName(self, instances):
        ProductCategoryName = instances.CategoryName
        return ProductCategoryName