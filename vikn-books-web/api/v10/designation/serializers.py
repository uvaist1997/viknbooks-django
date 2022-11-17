from rest_framework import serializers
from brands.models import Designation, Department


class DesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = ('id','BranchID','DesignationName','Notes')


class DesignationRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = ('id','DesignationID','BranchID','DesignationName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')



class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id','BranchID','DepartmentName','Notes')


class DepartmentRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id','DepartmentID','BranchID','DepartmentName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')
