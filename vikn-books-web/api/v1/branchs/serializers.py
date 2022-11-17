from rest_framework import serializers
from brands.models import Branch


class BranchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id','BranchName','BranchLocation')


class BranchRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = ('id','BranchID','BranchName','BranchLocation','CreatedUserID','CreatedDate','UpdatedDate','Action')
