from rest_framework import serializers
from brands.models import Branch


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id', 'BranchName', 'Building', 'City', 'state', 'country', 'PostalCode', 'Phone',
                  'Email', 'is_regional_office', 'regional_office', 'VATNumber', 'GSTNumber', 'is_gst', 'is_vat')


class BranchRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id', 'BranchID', 'BranchName', 'Building', 'City', 'state', 'country', 'PostalCode', 'Phone', 'Email', 'is_regional_office',
                  'regional_office', 'VATNumber', 'GSTNumber', 'is_gst', 'is_vat', 'CreatedUserID', 'CreatedDate', 'UpdatedDate', 'Action')
