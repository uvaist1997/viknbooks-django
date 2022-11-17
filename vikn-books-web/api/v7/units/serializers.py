from rest_framework import serializers
from brands.models import Unit,UQCTable
from rest_framework.fields import CurrentUserDefault


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ('id','BranchID','UnitName','Notes','UQC')


class UnitRestSerializer(serializers.ModelSerializer):
    UQC_Name = serializers.SerializerMethodField()
    class Meta:
        model = Unit
        fields = ('id','UnitID','BranchID','UnitName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action','UQC','UQC_Name')

    def get_UQC_Name(self, instances):
        UQC = instances.UQC
        # UQC_Name = ""
        # if UQCTable.objects.filter(id=UQC).exist():
        #     UQC_Name = UQCTable.objects.get(id=UQC).UQC_Name
        return str(UQC)


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()

