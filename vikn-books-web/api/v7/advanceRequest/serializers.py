from rest_framework import serializers
from brands.models import AdvanceRequest


class AdvanceRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvanceRequest
        fields = ('id','BranchID','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate')




class AdvanceRequestRestSerializer(serializers.ModelSerializer):
    EmployeeName = serializers.SerializerMethodField()

    class Meta:
        model = AdvanceRequest
        fields = ('id','AdvanceRequestID','BranchID','Status','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','EmployeeName','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_EmployeeName(self, instances):
        name = instances.EmployeeId.FirstName
        return name


class AdvanceApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvanceRequest
        fields = ('id','BranchID','Status','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate','Action')