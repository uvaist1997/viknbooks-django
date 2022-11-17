from rest_framework import serializers
from brands.models import Branch, BranchSettings


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id', 'BranchName', 'DisplayName', 'Building', 'City', 'state', 'country', 'PostalCode', 'Phone',
                  'Email', 'is_regional_office', 'regional_office', 'VATNumber', 'GSTNumber', 'is_gst', 'is_vat')


class BranchRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id', 'CompanyID', 'DisplayName', 'BranchID', 'BranchName', 'Building', 'City', 'state', 'country', 'PostalCode', 'Phone', 'Email', 'is_regional_office',
                  'regional_office', 'VATNumber', 'GSTNumber', 'is_gst', 'is_vat', 'CreatedUserID', 'CreatedDate', 'UpdatedDate', 'Action', 'vat_on_sales', 'vat_on_purchase', 'vat_on_expense', 'central_gst_on_purchase', 'state_gst_on_purchase', 'integrated_gst_on_purchase', 'central_gst_on_sales', 'state_gst_on_sales', 'integrated_gst_on_sales', 'central_gst_on_expense', 'state_gst_on_payment', 'round_off_sales', 'discount_on_sales', 'discount_on_purchase', 'discount_on_payment', 'discount_on_receipt', 'discount_on_loyalty', 'round_off_purchase')


class BranchSettingsSerializer(serializers.ModelSerializer):
    suppliersForAllBranches = serializers.BooleanField()
    customersForAllBranches = serializers.BooleanField()
    productsForAllBranches = serializers.BooleanField()
