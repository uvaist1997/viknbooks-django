from rest_framework import serializers
from brands.models import SalaryKit,SalaryKitDetails,SalaryComponent


class SalaryKitSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryKit
        fields = ('id','BranchID','EmployeeId','EmployeeCode','CategoryId','DepartmentID','DesignationID','BasicSalaryId','Type','SalaryFreequency','SalaryComponentType','Date',)


class SalaryKitRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryKit
        fields = ('id','SalaryKitID','BranchID','DepartmentID','CategoryId','DesignationID','BasicSalaryId','Type','SalaryFreequency','SalaryComponentType','Date','CreatedUserID','CreatedDate','UpdatedDate','Action')


class SalaryKitDetailsRestSerializer(serializers.ModelSerializer):
    detailID = serializers.SerializerMethodField()

    class Meta:
        model = SalaryKitDetails
        fields = ('id','detailID','SalaryKitID','SalaryComponentID','ExpressionType','ComponentType','Amount')

    def get_detailID(self, instances):
        return 0


class SalaryKitSingleSerializer(serializers.ModelSerializer):
    SalaryKitDetails = serializers.SerializerMethodField()
    BasicSalaryAmount = serializers.SerializerMethodField()

    class Meta:
        model = SalaryKit
        fields = ('id','SalaryKitDetails','BasicSalaryAmount','BranchID','EmployeeId','EmployeeCode','CategoryId','DepartmentID','DesignationID','BasicSalaryId','Type','SalaryFreequency','SalaryComponentType','Date',)

    def get_SalaryKitDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        SalaryKitID = instances.SalaryKitID
        sales_details = SalaryKitDetails.objects.filter(
             SalaryKitID=SalaryKitID)
        serialized = SalaryKitDetailsRestSerializer(sales_details, many=True,context={"CompanyID": CompanyID,
                                                                                   "PriceRounding": PriceRounding, })
        return serialized.data

    def get_BasicSalaryAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        BasicSalaryAmount = instances.BasicSalaryId.ExpressionValue
        print(BasicSalaryAmount,'BasicSalaryAmount================================')
        # details = SalaryComponent.objects.filter(
        #      pk=BasicSalaryId)

        return BasicSalaryAmount


