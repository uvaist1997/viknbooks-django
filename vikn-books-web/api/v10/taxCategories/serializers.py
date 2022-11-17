from rest_framework import serializers

from brands.models import (
    Product,
    PurchaseDetails,
    PurchaseOrderDetails,
    PurchaseReturnDetails,
    SalesDetails,
    SalesEstimateDetails,
    SalesOrderDetails,
    SalesReturnDetails,
    TaxCategory,
    TaxType,
)


class TaxCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxCategory
        fields = (
            "id",
            "BranchID",
            "TaxName",
            "TaxType",
            "PurchaseTax",
            "SalesTax",
            "Inclusive",
            "CreatedUserID",
        )


class TaxCategoryRestSerializer(serializers.ModelSerializer):

    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    TaxType = serializers.SerializerMethodField()
    TaxTypeID = serializers.SerializerMethodField()
    is_used = serializers.SerializerMethodField()

    class Meta:
        model = TaxCategory
        fields = (
            "id",
            "TaxID",
            "BranchID",
            "TaxName",
            "TaxType",
            "TaxTypeID",
            "PurchaseTax",
            "SalesTax",
            "Inclusive",
            "CreatedUserID",
            "CreatedDate",
            "UpdatedDate",
            "Action",
            "is_used",
            "IsDefault",
        )

    def get_is_used(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        TaxID = instances.TaxID
        is_used = False
        sales_count = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        purchase_count = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        salesReturn_count = SalesReturnDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        purchaseReturn_count = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        salesOrder_count = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        purchaseOrder_count = PurchaseOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()
        salesEstimate_count = SalesEstimateDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductTaxID=TaxID
        ).count()

        product_gst_count = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, GST=TaxID
        ).count()
        product_vat_count = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VatID=TaxID
        ).count()

        if (
            sales_count > 0
            or purchase_count > 0
            or salesReturn_count > 0
            or purchaseReturn_count > 0
            or salesOrder_count > 0
            or purchaseOrder_count > 0
            or salesEstimate_count > 0
            or product_gst_count > 0
            or product_vat_count > 0
        ):
            is_used = True

        return is_used

    def get_PurchaseTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        PurchaseTax = instances.PurchaseTax

        PurchaseTax = round(PurchaseTax, PriceRounding)

        return str(PurchaseTax)

    def get_SalesTax(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        SalesTax = instances.SalesTax

        SalesTax = round(SalesTax, PriceRounding)

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

        if TaxType.objects.filter(CompanyID=CompanyID, TaxTypeID=tax).exists():
            type_instance = TaxType.objects.get(CompanyID=CompanyID, TaxTypeID=tax)

            TaxTypeName = type_instance.TaxTypeName

        return TaxTypeName


class ListSerializerTaxType(serializers.Serializer):

    BranchID = serializers.IntegerField()
    TaxType = serializers.IntegerField()


class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxCategory
        fields = (
            "id",
            "TaxID",
            "TaxName",
            "TaxType",
            "PurchaseTax",
            "SalesTax",
            "Inclusive",
            "IsDefault",
        )


class ListTaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        fields = ("id", "TaxTypeID", "BranchID", "TaxTypeName", "Active")
