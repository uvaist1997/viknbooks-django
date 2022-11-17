from rest_framework import serializers
from brands.models import LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = ('id','BranchID','Name','Type')


class LeaveTypeRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = ('id','LeaveTypeID','BranchID','Name','Type','CreatedUserID','CreatedDate','UpdatedDate','Action')


