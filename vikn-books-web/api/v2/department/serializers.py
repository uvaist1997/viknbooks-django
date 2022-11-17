from rest_framework import serializers
from brands.models import Designation, Department


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id','BranchID','DepartmentName','Notes','ParentDepartment')


class DepartmentRestSerializer(serializers.ModelSerializer):
    ParentDepartmentName = serializers.SerializerMethodField()
    class Meta:
        model = Department
        fields = ('id','DepartmentID','BranchID','DepartmentName','ParentDepartment','ParentDepartmentName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')

    def get_ParentDepartmentName(self, instance):
        CompanyID = self.context.get("CompanyID")

        DepartmentID = instance.DepartmentID
        BranchID = instance.BranchID
        ParentDepartmentName = "Not Found"
        if Department.objects.filter(DepartmentID=DepartmentID,BranchID=BranchID,CompanyID=CompanyID).exists():
            DepartmentInstances = Department.objects.filter(DepartmentID=DepartmentID,BranchID=BranchID,CompanyID=CompanyID)
            for instance in DepartmentInstances:
                if instance.ParentDepartment:
                    ParentDepartmentName = instance.ParentDepartment.DepartmentName
                else: 
                    ParentDepartmentName = "Not Found"

            return ParentDepartmentName
        elif Department.objects.get(pk=instance.pk).ParentDepartment :
            ParentDepartmentName = Department.objects.get(pk=instance.pk).ParentDepartment.DepartmentName
            return ParentDepartmentName
        return "Not Found"