from rest_framework import serializers
from brands.models import PaymentMaster


class PaymentMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMaster
        fields = ('id','BranchID','Action','VoucherNo','VoucherType','LedgerID',
            'EmployeeID','PaymentNo',
            'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','CreatedUserID')


class PaymentMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMaster
        fields = ('id','PaymentMasterID','BranchID','Action','VoucherNo','VoucherType','LedgerID',
            'EmployeeID','PaymentNo',
            'FinancialYearID','Date','TotalAmount','Notes','IsActive','CreatedDate','CreatedUserID')
