from rest_framework import serializers
from brands.models import AttendanceMaster,AttendanceDetail


class AttendanceMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceMaster
        fields = ('id','BranchID','Shift','DepartmentID','DesignationID','CategoryId')



class AttendanceMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceMaster
        fields = ('id','AttendanceMasterID','BranchID','Shift','Date','DepartmentID','DesignationID','CategoryId','CreatedUserID','CreatedDate','UpdatedDate','Action')


class AttendanceDetailSerializer(serializers.ModelSerializer):
    detailID = serializers.SerializerMethodField()
    Employeepk = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceDetail
        fields = ('id','detailID','Employeepk','EmployeeId','EmployeeCode','Status','ShiftStartTime','ShiftEndTime')

    def get_Employeepk(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        pk = str(instances.EmployeeId.id)
        print(pk,"QQQQQQQQQQQQQQQQQQQQQQQQQ")
        
        return pk

    def get_detailID(self, instances):
        return 0


class AttendanceSingleSerializer(serializers.ModelSerializer):
    AttendanceDetails = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceMaster
        fields = ('id','AttendanceMasterID','AttendanceDetails','BranchID','Shift','Date','DepartmentID','DesignationID','CategoryId','CreatedUserID','CreatedDate','UpdatedDate','Action')

    def get_AttendanceDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        pk = instances.pk
        sales_details = AttendanceDetail.objects.filter(
             AttendanceId=pk)
        print(sales_details,'AttendanceId??????????????????????????????',pk)
        serialized = AttendanceDetailSerializer(sales_details, many=True,context={"CompanyID": CompanyID,
                                                                                   "PriceRounding": PriceRounding, })
        return serialized.data

  