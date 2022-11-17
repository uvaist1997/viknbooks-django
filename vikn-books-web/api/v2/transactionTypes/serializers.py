from rest_framework import serializers
from brands.models import TransactionTypes, MasterType


class TransactionTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionTypes
        fields = ('id','BranchID','MasterTypeID','Name','Notes','CreatedUserID','IsDefault')


class TransactionTypesRestSerializer(serializers.ModelSerializer):

    MasterTypeName = serializers.SerializerMethodField()

    class Meta:
        model = TransactionTypes
        fields = ('id','TransactionTypesID','BranchID','Action','MasterTypeID','MasterTypeName','Name','Notes','Action','CreatedDate','UpdatedDate','CreatedUserID','IsDefault')


    def get_MasterTypeName(self, instances):

        CompanyID = self.context.get("CompanyID")

        MasterTypeID = instances.MasterTypeID
        BranchID = instances.BranchID

        master_type = MasterType.objects.get(CompanyID=CompanyID,MasterTypeID=MasterTypeID,BranchID=BranchID)

        MasterTypeName = master_type.Name

        return MasterTypeName


class ListSerializerByMasterName(serializers.Serializer):

    BranchID = serializers.IntegerField()
    MasterName = serializers.CharField()