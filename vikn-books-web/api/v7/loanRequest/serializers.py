from rest_framework import serializers
from brands.models import LoanRequest


class LoanRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanRequest
        fields = ('id','BranchID','LoanTypeID','Interest','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate')




class LoanRequestRestSerializer(serializers.ModelSerializer):
    EmployeeName = serializers.SerializerMethodField()

    class Meta:
        model = LoanRequest
        fields = ('id','LoanRequestID','BranchID','LoanTypeID','Interest','Status','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','EmployeeName','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate','CreatedUserID','CreatedDate','UpdatedDate','Action')


    def get_EmployeeName(self, instances):
        name = instances.EmployeeId.FirstName
        return name


class LoanApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanRequest
        fields = ('id','BranchID','LoanTypeID','Status','Interest','EmployeeId','ModeOfPayment','PaymentAmount','PaymentAccount','Amount','NumOfInstalment','InstalmentAmount','RepaymentDate')