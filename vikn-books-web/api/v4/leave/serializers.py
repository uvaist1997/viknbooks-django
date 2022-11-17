from rest_framework import serializers
from brands.models import Leave,LeaveDetails


class LeaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leave
        fields = ('id','BranchID','Balance','FinancialYear','PreviousYear','Type','DepartmentID','DesignationID','EmployeeId','EmployeeCode','CategoryId')
        

class LeaveRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Leave
        fields = ('id','LeaveID','BranchID','Balance','FinancialYear','PreviousYear','Type','DepartmentID','DesignationID','EmployeeId','EmployeeCode','CategoryId','CreatedUserID','CreatedDate','UpdatedDate','Action')


class LeaveDetailsRestSerializer(serializers.ModelSerializer):
    detailID = serializers.SerializerMethodField()

    class Meta:
        model = LeaveDetails
        fields = ('id','detailID','LeaveID','Type','LeaveTypeID','Days')

    def get_detailID(self, instances):
        return 0


class LeaveSingleSerializer(serializers.ModelSerializer):
    LeaveDetails = serializers.SerializerMethodField()

    class Meta:
        model = Leave
        fields = ('id','BranchID','LeaveDetails','Balance','FinancialYear','PreviousYear','Type','DepartmentID','DesignationID','EmployeeId','EmployeeCode','CategoryId')

    def get_LeaveDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        pk = instances.pk
        sales_details = LeaveDetails.objects.filter(
             LeaveID=pk)
        print(sales_details,'LeaveID??????????????????????????????',pk)
        serialized = LeaveDetailsRestSerializer(sales_details, many=True,context={"CompanyID": CompanyID,
                                                                                   "PriceRounding": PriceRounding, })
        return serialized.data

  