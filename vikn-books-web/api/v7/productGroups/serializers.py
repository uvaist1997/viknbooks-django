from rest_framework import serializers
from brands.models import ProductGroup, ProductCategory
from api.v7.productCategories.serializers import ProductCategoryRestSerializer


class ProductGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductGroup
        fields = ('id', 'BranchID', 'GroupName',
                  'CategoryID', 'Notes', 'CreatedUserID')


class ProductGroupRestSerializer(serializers.ModelSerializer):

    ProductCategoryName = serializers.SerializerMethodField()
    ProductCategoryID = serializers.SerializerMethodField()
    KitchenName = serializers.SerializerMethodField()
    KitchenID = serializers.SerializerMethodField()

    class Meta:
        model = ProductGroup
        fields = ('id', 'ProductGroupID', 'BranchID', 'GroupName', 'CategoryID', 'ProductCategoryID','KitchenName','KitchenID',
                  'ProductCategoryName', 'Notes', 'CreatedUserID', 'CreatedDate', 'UpdatedDate', 'Action')

    def get_ProductCategoryName(self, instances):
        CompanyID = self.context.get("CompanyID")
        CategoryID = instances.CategoryID
        BranchID = instances.BranchID

        category = ProductCategory.objects.get(
            CompanyID=CompanyID, ProductCategoryID=CategoryID, BranchID=BranchID)

        CategoryName = category.CategoryName

        return CategoryName

    def get_ProductCategoryID(self, instances):
        ProductCategoryID = instances.CategoryID
        return ProductCategoryID

    def get_KitchenID(self, instances):
        KitchenID = ""
        if instances.kitchen:
            KitchenID = instances.kitchen.id
        return KitchenID


    def get_KitchenName(self, instances):
        KitchenName = ""
        if instances.kitchen:
            KitchenName = instances.kitchen.KitchenName
        return KitchenName
