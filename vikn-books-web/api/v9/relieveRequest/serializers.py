from rest_framework import serializers
from brands.models import RelieveRequest


class RelieveRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelieveRequest
        fields = ('id','BranchID','EmployeeId','RequestDate','Reportto','ReliveType','ReasonforRelive')



class RelieveRequestRestSerializer(serializers.ModelSerializer):
    EmployeeName = serializers.SerializerMethodField()
    RelieveTypeName = serializers.SerializerMethodField()

    class Meta:
        model = RelieveRequest
        fields = ('id','RelieveRequestID','RelieveTypeName','BranchID','Status','EmployeeName','EmployeeId','RequestDate','Reportto','ReliveType','ReasonforRelive','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_EmployeeName(self, instances):
        name = instances.EmployeeId.FirstName
        return name

    def get_RelieveTypeName(self, instances):
        name = instances.ReliveType
        return name


class RelieveApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelieveRequest
        fields = ('id','BranchID','EmployeeId','RequestDate','Reportto','ReliveType','ReasonforRelive','Status','ReasonforApprove')