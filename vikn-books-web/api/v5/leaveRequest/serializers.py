from rest_framework import serializers
from brands.models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequest
        fields = ('id','BranchID','EmployeeId','FromDate','ToDate','Reportto','LeaveTypeID','ReasonforLeave')



class LeaveRequestRestSerializer(serializers.ModelSerializer):
    EmployeeName = serializers.SerializerMethodField()
    LeaveTypeName = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = ('id','LeaveRequestID','BranchID','Status','ReasonforApprove','EmployeeName','EmployeeId','FromDate','ToDate','Reportto','LeaveTypeName','LeaveTypeID','ReasonforLeave','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_EmployeeName(self, instances):
        name = instances.EmployeeId.FirstName
        return name

    def get_LeaveTypeName(self, instances):
        name = instances.LeaveTypeID.Name
        return name


class LeaveApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequest
        fields = ('id','BranchID','EmployeeId','FromDate','ToDate','Reportto','LeaveTypeID','ReasonforLeave','Status','ReasonforApprove')